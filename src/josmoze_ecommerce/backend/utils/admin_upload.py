"""
🔧 GESTIONNAIRE UPLOAD ADMINISTRATEUR - JOSMOZE.COM
Interface d'administration pour upload manuel images/vidéos produits
"""

import os
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import HTTPException, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorClient
import aiofiles

# Configuration
MONGO_URL = os.environ.get("MONGO_URI", os.environ.get("MONGO_URL", ""))
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

# Dossiers de stockage
UPLOAD_DIR = Path("/app/backend/static/uploads")
IMAGES_DIR = UPLOAD_DIR / "images"
VIDEOS_DIR = UPLOAD_DIR / "videos"

# Créer les dossiers si inexistants
UPLOAD_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Types de fichiers supportés
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class AdminUploadManager:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def initialize(self):
        """Initialiser la connexion MongoDB"""
        if not self.client:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            
    async def upload_media_file(
        self, 
        file: UploadFile, 
        product_id: Optional[str] = None,
        media_type: str = "image",
        description: Optional[str] = None
    ) -> dict:
        """
        📤 Upload d'un fichier média (image ou vidéo)
        
        Args:
            file: Fichier uploadé
            product_id: ID du produit associé (optionnel)
            media_type: Type de média ('image' ou 'video')
            description: Description du média
            
        Returns:
            Dict avec informations du fichier uploadé
        """
        await self.initialize()
        
        # Validation du fichier
        file_extension = Path(file.filename).suffix.lower()
        
        if media_type == "image" and file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(400, f"Format image non supporté. Formats acceptés: {ALLOWED_IMAGE_EXTENSIONS}")
            
        if media_type == "video" and file_extension not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(400, f"Format vidéo non supporté. Formats acceptés: {ALLOWED_VIDEO_EXTENSIONS}")
            
        # Validation taille
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, f"Fichier trop volumineux. Taille max: {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Génération nom unique
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        
        # Chemin de stockage
        storage_dir = IMAGES_DIR if media_type == "image" else VIDEOS_DIR
        file_path = storage_dir / filename
        
        # Sauvegarde physique
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
            
        # URL d'accès public
        public_url = f"/static/uploads/{media_type}s/{filename}"
        
        # Métadonnées
        media_info = {
            "id": file_id,
            "filename": filename,
            "original_name": file.filename,
            "file_path": str(file_path),
            "public_url": public_url,
            "media_type": media_type,
            "file_size": len(content),
            "file_extension": file_extension,
            "product_id": product_id,
            "description": description,
            "upload_date": datetime.now(),
            "status": "active"
        }
        
        # Sauvegarde en base
        await self.db.media_library.insert_one(media_info)
        
        # Si associé à un produit, mettre à jour le produit
        if product_id:
            await self._update_product_media(product_id, media_info)
            
        logging.info(f"✅ Fichier uploadé: {filename} ({len(content)} bytes)")
        
        return {
            "success": True,
            "media_id": file_id,
            "filename": filename,
            "public_url": public_url,
            "file_size": len(content),
            "media_type": media_type,
            "message": f"Fichier {media_type} uploadé avec succès"
        }
        
    async def _update_product_media(self, product_id: str, media_info: dict):
        """Associer un média à un produit"""
        update_field = "images" if media_info["media_type"] == "image" else "videos"
        
        await self.db.products.update_one(
            {"id": product_id},
            {
                "$push": {
                    update_field: {
                        "url": media_info["public_url"],
                        "description": media_info["description"],
                        "upload_date": media_info["upload_date"]
                    }
                }
            }
        )
        
    async def get_media_library(self, media_type: Optional[str] = None, product_id: Optional[str] = None) -> List[dict]:
        """📚 Récupérer la bibliothèque de médias"""
        await self.initialize()
        
        query = {"status": "active"}
        if media_type:
            query["media_type"] = media_type
        if product_id:
            query["product_id"] = product_id
            
        cursor = self.db.media_library.find(query).sort("upload_date", -1)
        media_list = await cursor.to_list(length=None)
        
        return media_list
        
    async def delete_media(self, media_id: str) -> dict:
        """🗑️ Supprimer un média"""
        await self.initialize()
        
        # Récupérer info média
        media = await self.db.media_library.find_one({"id": media_id})
        if not media:
            raise HTTPException(404, "Média non trouvé")
            
        # Supprimer fichier physique
        file_path = Path(media["file_path"])
        if file_path.exists():
            file_path.unlink()
            
        # Marquer comme supprimé en base
        await self.db.media_library.update_one(
            {"id": media_id},
            {"$set": {"status": "deleted", "deleted_date": datetime.now()}}
        )
        
        return {"success": True, "message": "Média supprimé avec succès"}
        
    async def update_product_image(self, product_id: str, new_image_url: str) -> dict:
        """🔄 Mettre à jour l'image principale d'un produit"""
        await self.initialize()
        
        result = await self.db.products.update_one(
            {"id": product_id},
            {"$set": {"image": new_image_url, "last_updated": datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(404, "Produit non trouvé")
            
        return {"success": True, "message": "Image produit mise à jour"}

# Instance globale
admin_upload_manager = AdminUploadManager()

async def get_admin_upload_manager():
    """Factory pour récupérer le gestionnaire d'upload"""
    return admin_upload_manager
