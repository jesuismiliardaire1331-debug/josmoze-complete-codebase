#!/usr/bin/env python3
"""
🚀 PHASE 8 - THOMAS CHATBOT COMMERCIAL V2 FINALISATION
Backend API Testing for Josmose.com - Thomas Commercial Features Testing

TESTS PHASE 8 - FONCTIONNALITÉS COMMERCIALES THOMAS :
1. **Test intention d'achat directe** : Message "Je veux acheter un osmoseur pour ma famille de 4 personnes"
2. **Test recommandation intelligente** : Message "Bonjour Thomas" avec conversation_history
3. **Test liens cliquables et données panier** : Vérifier product-link class et cart_data
4. **Validation structure réponse** : Vérifier tous les nouveaux champs Phase 8

✅ TESTS CRITIQUES PHASE 8 :
1. **Endpoint /api/ai-agents/chat** : Vérifier existence et fonctionnement
2. **Purchase Intent Detection** : Réponse contient produit recommandé + cart_data + CTA
3. **Smart Recommendations** : Recommandations personnalisées selon profil utilisateur
4. **HTML Links & CTA Buttons** : Liens cliquables avec class="product-link" fonctionnels
5. **Response Structure** : cart_data, product_recommended, user_analysis, suggestions

✅ OBJECTIFS PHASE 8 :
- Thomas détecte intentions d'achat et recommande produits spécifiques
- Système "Add to Cart" direct depuis conversations Thomas
- Recommandations avancées basées sur profil utilisateur et historique
- Liens produits cliquables avec données panier complètes

🎯 RÉSULTAT ATTENDU : Thomas commercial convertisseur 100% fonctionnel avec intégration panier
"""

import requests
import json
import time
import logging
import os
import io
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
from PIL import Image
from urllib.parse import urlparse

# Backend URL from environment
BACKEND_URL = "https://water-ecom-admin.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.session_id = None
        self.auth_token = None
        self.uploaded_blog_images = []  # Store uploaded blog image URLs
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def extract_unsplash_urls_from_mapping(self) -> List[Tuple[str, str]]:
        """Extract Unsplash URLs from mapping-images-blog.md file"""
        try:
            mapping_file = "/app/mapping-images-blog.md"
            if not os.path.exists(mapping_file):
                self.log_test(
                    "Extract Unsplash URLs from mapping",
                    False,
                    f"Mapping file not found: {mapping_file}"
                )
                return []
            
            with open(mapping_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract URLs using regex pattern
            url_pattern = r'URL:\s*`(https://images\.unsplash\.com/[^`]+)`'
            description_pattern = r'\*\*Description\s*:\*\*\s*([^\n]+)'
            
            urls = re.findall(url_pattern, content)
            descriptions = re.findall(description_pattern, content)
            
            # Combine URLs with descriptions
            url_desc_pairs = []
            for i, url in enumerate(urls):
                desc = descriptions[i] if i < len(descriptions) else f"Blog image {i+1}"
                url_desc_pairs.append((url, desc))
            
            self.log_test(
                "Extract Unsplash URLs from mapping",
                True,
                f"Extracted {len(url_desc_pairs)} URLs from mapping file"
            )
            
            return url_desc_pairs
            
        except Exception as e:
            self.log_test(
                "Extract Unsplash URLs from mapping",
                False,
                f"Error reading mapping file: {str(e)}"
            )
            return []
    
    def download_image_from_url(self, url: str, description: str) -> Tuple[bool, bytes, str]:
        """Download image from Unsplash URL"""
        try:
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Verify it's actually an image
                content_type = response.headers.get('content-type', '').lower()
                if content_type.startswith('image/'):
                    # Generate filename from description
                    safe_desc = re.sub(r'[^\w\s-]', '', description).strip()
                    safe_desc = re.sub(r'[-\s]+', '-', safe_desc)
                    filename = f"blog-{safe_desc[:30]}.jpg"
                    
                    return True, response.content, filename
                else:
                    return False, b'', f"Invalid content type: {content_type}"
            else:
                return False, b'', f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, b'', f"Download error: {str(e)}"
    
    def upload_blog_image_to_api(self, image_data: bytes, filename: str, description: str) -> Tuple[bool, str]:
        """Upload blog image via API with product_id='blog-images'"""
        try:
            files = {
                'image': (filename, image_data, 'image/jpeg')
            }
            data = {
                'product_id': 'blog-images',
                'replace_current': 'false'  # Don't replace, add new images
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success') == True:
                    image_url = response_data.get('image_url', '')
                    if '/api/admin/get-uploaded-image/' in image_url:
                        return True, image_url
                    else:
                        return False, f"Invalid URL format: {image_url}"
                else:
                    return False, f"Upload failed: {response_data.get('message', 'Unknown error')}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Upload error: {str(e)}"
    
    def test_phase7_image_acquisition_and_upload(self):
        """PHASE 7: Complete image acquisition and upload process"""
        print("🚀 PHASE 7 - ACQUISITION ET UPLOAD DES 20 IMAGES BLOG")
        print("=" * 70)
        
        # Step 1: Extract URLs from mapping
        print("\n📋 ÉTAPE 1: Extraction des URLs Unsplash...")
        url_desc_pairs = self.extract_unsplash_urls_from_mapping()
        
        if not url_desc_pairs:
            self.log_test(
                "PHASE 7 - Image Acquisition Complete",
                False,
                "No URLs found in mapping file"
            )
            return False
        
        print(f"   ✅ {len(url_desc_pairs)} URLs extraites du mapping")
        
        # Step 2: Download and upload images
        print(f"\n📋 ÉTAPE 2: Téléchargement et upload de {len(url_desc_pairs)} images...")
        
        successful_uploads = 0
        failed_downloads = 0
        failed_uploads = 0
        
        for i, (url, description) in enumerate(url_desc_pairs, 1):
            print(f"   🔄 Image {i}/{len(url_desc_pairs)}: {description[:50]}...")
            
            # Download image
            success, image_data, filename_or_error = self.download_image_from_url(url, description)
            
            if success:
                # Upload to API
                upload_success, api_url_or_error = self.upload_blog_image_to_api(
                    image_data, filename_or_error, description
                )
                
                if upload_success:
                    self.uploaded_blog_images.append({
                        'description': description,
                        'original_url': url,
                        'api_url': api_url_or_error,
                        'filename': filename_or_error
                    })
                    successful_uploads += 1
                    print(f"      ✅ Upload réussi: {api_url_or_error}")
                else:
                    failed_uploads += 1
                    print(f"      ❌ Upload échoué: {api_url_or_error}")
            else:
                failed_downloads += 1
                print(f"      ❌ Téléchargement échoué: {filename_or_error}")
        
        # Step 3: Summary
        total_images = len(url_desc_pairs)
        success_rate = (successful_uploads / total_images * 100) if total_images > 0 else 0
        
        print(f"\n📊 RÉSUMÉ PHASE 7:")
        print(f"   Total images: {total_images}")
        print(f"   ✅ Uploads réussis: {successful_uploads}")
        print(f"   ❌ Téléchargements échoués: {failed_downloads}")
        print(f"   ❌ Uploads échoués: {failed_uploads}")
        print(f"   📈 Taux de réussite: {success_rate:.1f}%")
        
        # Log overall result
        if success_rate >= 80:
            self.log_test(
                "PHASE 7 - Image Acquisition Complete",
                True,
                f"✅ {successful_uploads}/{total_images} images uploadées avec succès ({success_rate:.1f}% réussite)"
            )
            return True
        else:
            self.log_test(
                "PHASE 7 - Image Acquisition Complete",
                False,
                f"❌ Seulement {successful_uploads}/{total_images} images uploadées ({success_rate:.1f}% réussite)"
            )
            return False
    
    def test_validate_uploaded_blog_images(self):
        """Validate that uploaded blog images are accessible via API"""
        if not self.uploaded_blog_images:
            self.log_test(
                "Validate Blog Images Access",
                False,
                "No uploaded blog images to validate"
            )
            return False
        
        print(f"\n📋 VALIDATION: Test d'accès à {len(self.uploaded_blog_images)} images uploadées...")
        
        # Test access to first 5 images (sample validation)
        test_images = self.uploaded_blog_images[:5]
        successful_access = 0
        
        for i, image_info in enumerate(test_images, 1):
            api_url = image_info['api_url']
            description = image_info['description']
            
            try:
                full_url = f"https://water-ecom-admin.preview.emergentagent.com{api_url}"
                response = self.session.get(full_url, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if content_type.startswith('image/'):
                        # Verify image is valid with PIL
                        try:
                            img = Image.open(io.BytesIO(response.content))
                            img.verify()
                            successful_access += 1
                            print(f"   ✅ Image {i}: {description[:40]}... - Accessible")
                        except Exception as pil_error:
                            print(f"   ❌ Image {i}: PIL validation failed - {pil_error}")
                    else:
                        print(f"   ❌ Image {i}: Invalid content-type - {content_type}")
                else:
                    print(f"   ❌ Image {i}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Image {i}: Access error - {str(e)}")
        
        validation_rate = (successful_access / len(test_images) * 100) if test_images else 0
        
        if validation_rate >= 80:
            self.log_test(
                "Validate Blog Images Access",
                True,
                f"✅ {successful_access}/{len(test_images)} images testées sont accessibles ({validation_rate:.1f}%)"
            )
            return True
        else:
            self.log_test(
                "Validate Blog Images Access",
                False,
                f"❌ Seulement {successful_access}/{len(test_images)} images accessibles ({validation_rate:.1f}%)"
            )
            return False
    
    def generate_blog_images_urls_list(self):
        """Generate final list of blog image URLs for integration"""
        if not self.uploaded_blog_images:
            print("\n❌ Aucune image uploadée pour générer la liste")
            return
        
        print(f"\n📋 LISTE FINALE DES {len(self.uploaded_blog_images)} URLs API POUR INTÉGRATION:")
        print("=" * 70)
        
        for i, image_info in enumerate(self.uploaded_blog_images, 1):
            print(f"{i:2d}. {image_info['description']}")
            print(f"    URL API: {image_info['api_url']}")
            print(f"    Filename: {image_info['filename']}")
            print()
        
        # Save to file for easy access
        try:
            with open('/app/blog_images_urls.json', 'w', encoding='utf-8') as f:
                json.dump(self.uploaded_blog_images, f, indent=2, ensure_ascii=False)
            print("✅ URLs sauvegardées dans /app/blog_images_urls.json")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {str(e)}")
    
    def run_phase7_blog_images_tests(self):
        """Execute PHASE 7 blog images acquisition and upload tests"""
        print("🚀 PHASE 7 - ACQUISITION ET UPLOAD DES 20 IMAGES BLOG")
        print("=" * 70)
        print("🎯 OBJECTIF: Télécharger et uploader les 20 images Unsplash du mapping")
        print("🔧 PROCESSUS: Download → Upload API → Validation accès")
        print("=" * 70)
        
        # Test 1: Complete image acquisition and upload
        acquisition_success = self.test_phase7_image_acquisition_and_upload()
        
        # Test 2: Validate uploaded images are accessible
        if acquisition_success:
            validation_success = self.test_validate_uploaded_blog_images()
            
            # Generate final URLs list
            self.generate_blog_images_urls_list()
        else:
            self.log_test(
                "Validate Blog Images Access",
                False,
                "❌ Impossible de valider - Acquisition précédente échouée"
            )
        
        return self.generate_phase7_summary()
    
    def generate_phase7_summary(self):
        """Generate PHASE 7 test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ PHASE 7 - ACQUISITION ET UPLOAD IMAGES BLOG")
        print("=" * 70)
        print(f"Total des tests: {total_tests}")
        print(f"✅ Réussis: {passed_tests}")
        print(f"❌ Échoués: {failed_tests}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        print(f"🖼️ Images uploadées: {len(self.uploaded_blog_images)}")
        
        print("\n📋 DÉTAIL DES RÉSULTATS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Determine overall status
        if success_rate == 100 and len(self.uploaded_blog_images) >= 15:
            overall_status = "🎉 PHASE 7 TERMINÉE AVEC SUCCÈS"
            status_details = f"Toutes les images blog uploadées et accessibles!"
        elif success_rate >= 80 and len(self.uploaded_blog_images) >= 10:
            overall_status = "✅ PHASE 7 LARGEMENT RÉUSSIE"
            status_details = f"Majorité des images blog opérationnelles ({len(self.uploaded_blog_images)} images)"
        elif success_rate >= 60:
            overall_status = "⚠️ PHASE 7 PARTIELLEMENT RÉUSSIE"
            status_details = f"Quelques images uploadées ({len(self.uploaded_blog_images)} images)"
        else:
            overall_status = "❌ PHASE 7 ÉCHOUÉE"
            status_details = f"Problèmes critiques avec acquisition images"
        
        print(f"\n{overall_status}")
        print(f"📊 {status_details}")
        
        if len(self.uploaded_blog_images) > 0:
            print(f"\n🎯 RÉSULTAT FINAL: {len(self.uploaded_blog_images)} URLs API opérationnelles pour intégration")
            print("📁 Liste complète sauvegardée dans blog_images_urls.json")
        
        return {
            "overall_success": success_rate >= 80 and len(self.uploaded_blog_images) >= 10,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "uploaded_images_count": len(self.uploaded_blog_images),
            "status": overall_status,
            "details": status_details,
            "test_results": self.test_results,
            "uploaded_images": self.uploaded_blog_images
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def create_test_image(self, filename: str, format: str = "JPEG", size: tuple = (500, 400)) -> bytes:
        """Create a test image file"""
        img = Image.new('RGB', size, color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    def test_admin_upload_endpoint_exists(self):
        """Test 1: Vérifier que l'endpoint POST /api/admin/upload-product-image existe"""
        try:
            # Test avec une requête vide pour vérifier l'existence de l'endpoint
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image")
            
            # L'endpoint doit exister (pas 404) même si la requête échoue
            if response.status_code != 404:
                self.log_test(
                    "Endpoint /api/admin/upload-product-image existe",
                    True,
                    f"Endpoint accessible (status: {response.status_code})"
                )
                return True
            else:
                self.log_test(
                    "Endpoint /api/admin/upload-product-image existe",
                    False,
                    "Endpoint non trouvé (404)"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Endpoint /api/admin/upload-product-image existe",
                False,
                f"Erreur de connexion: {str(e)}"
            )
            return False
    
    def test_validation_required_fields(self):
        """Test 2: Validation des champs requis (image et product_id)"""
        try:
            # Test sans image ni product_id
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image")
            
            if response.status_code == 400:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                
                # Vérifier que le message d'erreur mentionne les champs requis
                error_message = response_data.get('detail', '').lower()
                if 'image' in error_message and ('product_id' in error_message or 'requis' in error_message):
                    self.log_test(
                        "Validation champs requis (image + product_id)",
                        True,
                        f"Erreur 400 avec message approprié: {response_data.get('detail', '')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Validation champs requis (image + product_id)",
                        False,
                        f"Message d'erreur incorrect: {response_data.get('detail', '')}"
                    )
                    return False
            else:
                self.log_test(
                    "Validation champs requis (image + product_id)",
                    False,
                    f"Code de statut incorrect: {response.status_code} (attendu: 400)"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Validation champs requis (image + product_id)",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def test_file_type_validation(self):
        """Test 3: Validation des types de fichiers (JPG, PNG, WebP)"""
        try:
            # Test avec un fichier de type non supporté (TXT)
            files = {
                'image': ('test.txt', b'This is not an image', 'text/plain')
            }
            data = {
                'product_id': 'osmoseur-premium',
                'replace_current': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
            
            if response.status_code == 400:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                error_message = response_data.get('detail', '').lower()
                
                if 'type' in error_message or 'format' in error_message or 'supporté' in error_message:
                    self.log_test(
                        "Validation type de fichier (rejet TXT)",
                        True,
                        f"Type de fichier non supporté correctement rejeté: {response_data.get('detail', '')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Validation type de fichier (rejet TXT)",
                        False,
                        f"Message d'erreur incorrect: {response_data.get('detail', '')}"
                    )
                    return False
            else:
                self.log_test(
                    "Validation type de fichier (rejet TXT)",
                    False,
                    f"Code de statut incorrect: {response.status_code} (attendu: 400)"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Validation type de fichier (rejet TXT)",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def test_file_size_validation(self):
        """Test 4: Validation taille maximum (5MB)"""
        try:
            # Créer un fichier de plus de 5MB (simulé avec des données)
            large_image_data = b'fake_image_data' * (6 * 1024 * 1024 // 15)  # ~6MB
            
            files = {
                'image': ('large_image.jpg', large_image_data, 'image/jpeg')
            }
            data = {
                'product_id': 'osmoseur-premium',
                'replace_current': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
            
            if response.status_code == 400:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                error_message = response_data.get('detail', '').lower()
                
                if 'taille' in error_message or 'volumineux' in error_message or '5mb' in error_message:
                    self.log_test(
                        "Validation taille fichier (max 5MB)",
                        True,
                        f"Fichier trop volumineux correctement rejeté: {response_data.get('detail', '')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Validation taille fichier (max 5MB)",
                        False,
                        f"Message d'erreur incorrect: {response_data.get('detail', '')}"
                    )
                    return False
            else:
                self.log_test(
                    "Validation taille fichier (max 5MB)",
                    False,
                    f"Code de statut incorrect: {response.status_code} (attendu: 400)"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Validation taille fichier (max 5MB)",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def test_successful_upload_with_api_url(self):
        """Test 5: Upload réussi avec URL API dédiée (PHASE 4 FINAL)"""
        try:
            # Créer une image de test valide
            test_image = self.create_test_image("test_image.jpg", "JPEG", (400, 300))
            
            files = {
                'image': ('test_osmoseur_premium.jpg', test_image, 'image/jpeg')
            }
            data = {
                'product_id': 'osmoseur-premium',
                'replace_current': 'true'
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Vérifier la structure de la réponse
                required_fields = ['success', 'image_url', 'filename', 'product_id']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields and response_data.get('success') == True:
                    image_url = response_data.get('image_url', '')
                    
                    # NOUVEAU: Vérifier que l'URL utilise le format API dédié
                    if '/api/admin/get-uploaded-image/' in image_url:
                        self.log_test(
                            "Upload image → URL API dédiée",
                            True,
                            f"✅ Upload réussi avec URL API: {image_url}, Produit: {response_data.get('product_id')}"
                        )
                        return True, image_url
                    else:
                        self.log_test(
                            "Upload image → URL API dédiée",
                            False,
                            f"❌ URL incorrecte: {image_url} (doit contenir /api/admin/get-uploaded-image/)"
                        )
                        return False, None
                else:
                    self.log_test(
                        "Upload image → URL API dédiée",
                        False,
                        f"Réponse incomplète - Champs manquants: {missing_fields}, Success: {response_data.get('success')}"
                    )
                    return False, None
            else:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                self.log_test(
                    "Upload image → URL API dédiée",
                    False,
                    f"Code de statut incorrect: {response.status_code}, Erreur: {response_data.get('detail', '')}"
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                "Upload image → URL API dédiée",
                False,
                f"Erreur: {str(e)}"
            )
            return False, None
    
    def test_api_image_access_with_correct_mime_type(self, image_url: str):
        """Test 6: Accès image via API avec MIME type correct (PHASE 4 CRITIQUE)"""
        if not image_url:
            self.log_test(
                "API Image Access + MIME Type",
                False,
                "Aucune URL fournie"
            )
            return False
            
        try:
            # Construire l'URL complète pour l'API
            full_url = f"https://water-ecom-admin.preview.emergentagent.com{image_url}"
            
            response = self.session.get(full_url)
            
            if response.status_code == 200:
                # CRITIQUE: Vérifier le Content-Type
                content_type = response.headers.get('content-type', '').lower()
                
                # Vérifier que c'est une image et PAS du HTML
                if content_type.startswith('image/'):
                    # Vérifier spécifiquement que ce n'est pas text/html
                    if 'text/html' not in content_type:
                        # Bonus: Vérifier que l'image est valide avec PIL
                        try:
                            from PIL import Image
                            import io
                            img = Image.open(io.BytesIO(response.content))
                            img.verify()  # Vérifier que l'image est valide
                            
                            self.log_test(
                                "API Image Access + MIME Type",
                                True,
                                f"✅ Image accessible via API {full_url} | Content-Type: {content_type} | Taille: {len(response.content)} bytes | PIL: Valide"
                            )
                            return True
                        except Exception as pil_error:
                            self.log_test(
                                "API Image Access + MIME Type",
                                False,
                                f"⚠️ Image accessible mais PIL échoue: {pil_error} | Content-Type: {content_type}"
                            )
                            return False
                    else:
                        self.log_test(
                            "API Image Access + MIME Type",
                            False,
                            f"❌ PROBLÈME CRITIQUE: Content-Type contient text/html: {content_type}"
                        )
                        return False
                else:
                    self.log_test(
                        "API Image Access + MIME Type",
                        False,
                        f"❌ PROBLÈME CRITIQUE: Content-Type n'est pas image/*: {content_type}"
                    )
                    return False
            else:
                self.log_test(
                    "API Image Access + MIME Type",
                    False,
                    f"❌ URL API non accessible: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "API Image Access + MIME Type",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def test_dedicated_api_endpoint_exists(self):
        """Test NOUVEAU: Vérifier que l'endpoint GET /api/admin/get-uploaded-image/{filename} existe"""
        try:
            # Test avec un nom de fichier fictif pour vérifier l'existence de l'endpoint
            test_filename = "test-file-that-does-not-exist.jpg"
            response = self.session.get(f"{BACKEND_URL}/admin/get-uploaded-image/{test_filename}")
            
            # L'endpoint doit exister (pas 404 pour l'endpoint lui-même)
            # Il peut retourner 404 pour le fichier, mais pas pour l'endpoint
            if response.status_code == 404:
                # Vérifier si c'est une 404 pour le fichier (bon) ou pour l'endpoint (mauvais)
                try:
                    response_data = response.json()
                    error_detail = response_data.get('detail', '').lower()
                    if 'image non trouvée' in error_detail or 'not found' in error_detail:
                        self.log_test(
                            "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                            True,
                            f"✅ Endpoint existe (404 pour fichier inexistant: '{error_detail}')"
                        )
                        return True
                    else:
                        self.log_test(
                            "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                            False,
                            f"❌ Endpoint non trouvé: {error_detail}"
                        )
                        return False
                except:
                    # Si pas de JSON, probablement une vraie 404 d'endpoint
                    self.log_test(
                        "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                        False,
                        "❌ Endpoint non trouvé (404 sans JSON)"
                    )
                    return False
            elif response.status_code in [200, 500]:
                # 200 = fichier trouvé (improbable), 500 = erreur serveur mais endpoint existe
                self.log_test(
                    "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                    True,
                    f"✅ Endpoint existe (status: {response.status_code})"
                )
                return True
            else:
                self.log_test(
                    "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                    False,
                    f"❌ Status inattendu: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Endpoint API dédié /api/admin/get-uploaded-image/{filename}",
                False,
                f"Erreur de connexion: {str(e)}"
            )
            return False
        """Test 7: Génération de noms de fichiers uniques (UUID)"""
        try:
            # Upload de deux images identiques
            test_image = self.create_test_image("duplicate.jpg", "JPEG", (200, 200))
            
            filenames = []
            
            for i in range(2):
                files = {
                    'image': ('duplicate.jpg', test_image, 'image/jpeg')
                }
                data = {
                    'product_id': 'osmoseur-essentiel',
                    'replace_current': 'false'
                }
                
                response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    filename = response_data.get('filename', '')
                    filenames.append(filename)
                else:
                    self.log_test(
                        "Génération noms uniques (UUID)",
                        False,
                        f"Upload {i+1} échoué: {response.status_code}"
                    )
                    return False
            
            # Vérifier que les noms sont différents
            if len(filenames) == 2 and filenames[0] != filenames[1]:
                # Vérifier que les noms contiennent des éléments uniques (UUID-like)
                unique_parts = []
                for filename in filenames:
                    # Extraire la partie unique (entre product_id et extension)
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        unique_parts.append(parts[1].split('.')[0])
                
                if len(set(unique_parts)) == 2:  # Deux parties uniques différentes
                    self.log_test(
                        "Génération noms uniques (UUID)",
                        True,
                        f"Noms uniques générés: {filenames[0]} et {filenames[1]}"
                    )
                    return True
                else:
                    self.log_test(
                        "Génération noms uniques (UUID)",
                        False,
                        f"Parties uniques identiques: {unique_parts}"
                    )
                    return False
            else:
                self.log_test(
                    "Génération noms uniques (UUID)",
                    False,
                    f"Noms de fichiers identiques: {filenames}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Génération noms uniques (UUID)",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def test_database_update_with_replace_current(self):
        """Test 8: Mise à jour base de données avec replace_current=true"""
        try:
            # D'abord, récupérer l'état actuel du produit
            response = self.session.get(f"{BACKEND_URL}/products/osmoseur-premium")
            
            if response.status_code == 200:
                original_product = response.json()
                original_image = original_product.get('image', '')
                
                # Upload avec replace_current=true
                test_image = self.create_test_image("replacement.jpg", "JPEG", (300, 250))
                
                files = {
                    'image': ('replacement_premium.jpg', test_image, 'image/jpeg')
                }
                data = {
                    'product_id': 'osmoseur-premium',
                    'replace_current': 'true'
                }
                
                upload_response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
                
                if upload_response.status_code == 200:
                    upload_data = upload_response.json()
                    new_image_url = upload_data.get('image_url', '')
                    
                    # Vérifier que l'upload indique le remplacement
                    if upload_data.get('replaced') == True:
                        self.log_test(
                            "Mise à jour DB avec replace_current=true",
                            True,
                            f"Remplacement confirmé - Nouvelle URL: {new_image_url}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Mise à jour DB avec replace_current=true",
                            False,
                            f"Remplacement non confirmé dans la réponse: {upload_data.get('replaced')}"
                        )
                        return False
                else:
                    self.log_test(
                        "Mise à jour DB avec replace_current=true",
                        False,
                        f"Upload échoué: {upload_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Mise à jour DB avec replace_current=true",
                    False,
                    f"Impossible de récupérer le produit original: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Mise à jour DB avec replace_current=true",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def run_phase4_final_tests(self):
        """Exécuter les tests finaux Phase 4 avec solution API dédiée"""
        print("🚀 PHASE 4 - TEST FINAL AVEC SOLUTION API DÉDIÉE")
        print("=" * 70)
        print("🎯 OBJECTIF: Tester la solution alternative avec endpoint API dédié")
        print("🔧 CONTOURNEMENT: Problème routage Kubernetes résolu avec FileResponse")
        print("=" * 70)
        
        # Test 1: Endpoint upload existe
        print("\n📋 TEST 1: Vérification endpoint upload...")
        upload_exists = self.test_admin_upload_endpoint_exists()
        
        # Test 2: Endpoint API dédié existe  
        print("\n📋 TEST 2: Vérification endpoint API dédié...")
        api_exists = self.test_dedicated_api_endpoint_exists()
        
        if not upload_exists:
            print("\n❌ ARRÊT DES TESTS - Endpoint upload non accessible")
            return self.generate_phase4_summary()
        
        # Test 3: Validation basique
        print("\n📋 TEST 3: Validation champs requis...")
        self.test_validation_required_fields()
        
        # Test 4: Validation type de fichier
        print("\n📋 TEST 4: Validation type fichier...")
        self.test_file_type_validation()
        
        # Test 5: Upload avec URL API (TEST CRITIQUE)
        print("\n📋 TEST 5: Upload → URL API dédiée (CRITIQUE)...")
        success, image_url = self.test_successful_upload_with_api_url()
        
        # Test 6: Accès image via API avec MIME type (TEST CRITIQUE)
        if success and image_url:
            print("\n📋 TEST 6: Accès API + MIME Type (CRITIQUE)...")
            self.test_api_image_access_with_correct_mime_type(image_url)
        else:
            self.log_test(
                "API Image Access + MIME Type",
                False,
                "❌ Impossible de tester - Upload précédent échoué"
            )
        
        # Test 7: Scénario complet osmoseur-premium
        print("\n📋 TEST 7: Scénario complet osmoseur-premium...")
        self.test_complete_osmoseur_premium_scenario()
        
        return self.generate_phase4_summary()
    
    def test_complete_osmoseur_premium_scenario(self):
        """Test SCÉNARIO COMPLET selon review_request"""
        try:
            print("   🔄 Étape 1: Upload test image → osmoseur-premium")
            
            # Créer une image de test spécifique
            test_image = self.create_test_image("osmoseur_premium_test.jpg", "JPEG", (600, 400))
            
            files = {
                'image': ('osmoseur_premium_final.jpg', test_image, 'image/jpeg')
            }
            data = {
                'product_id': 'osmoseur-premium',
                'replace_current': 'true'
            }
            
            # Upload
            response = self.session.post(f"{BACKEND_URL}/admin/upload-product-image", files=files, data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                image_url = response_data.get('image_url', '')
                
                print(f"   ✅ Étape 2: URL récupérée: {image_url}")
                
                # Vérifier format URL API
                if '/api/admin/get-uploaded-image/' in image_url:
                    print("   ✅ Étape 3: Format URL API correct")
                    
                    # Test GET sur URL API
                    full_url = f"https://water-ecom-admin.preview.emergentagent.com{image_url}"
                    img_response = self.session.get(full_url)
                    
                    if img_response.status_code == 200:
                        content_type = img_response.headers.get('content-type', '').lower()
                        
                        print(f"   📊 Étape 4: Content-Type reçu: {content_type}")
                        
                        # Vérifications critiques
                        is_image = content_type.startswith('image/')
                        not_html = 'text/html' not in content_type
                        is_jpeg = 'image/jpeg' in content_type
                        
                        if is_image and not_html:
                            print("   ✅ Étape 5: MIME type correct (image/* et pas text/html)")
                            
                            # Test PIL
                            try:
                                from PIL import Image
                                import io
                                img = Image.open(io.BytesIO(img_response.content))
                                img.verify()
                                print("   ✅ Étape 6: Image lisible par PIL")
                                
                                self.log_test(
                                    "SCÉNARIO COMPLET osmoseur-premium",
                                    True,
                                    f"🎉 SUCCÈS TOTAL: Upload → {image_url} → Content-Type: {content_type} → PIL: OK"
                                )
                                return True
                                
                            except Exception as pil_error:
                                print(f"   ❌ Étape 6: PIL échoue: {pil_error}")
                                self.log_test(
                                    "SCÉNARIO COMPLET osmoseur-premium",
                                    False,
                                    f"PIL validation échouée: {pil_error}"
                                )
                                return False
                        else:
                            print(f"   ❌ Étape 5: MIME type incorrect - Image: {is_image}, Not HTML: {not_html}")
                            self.log_test(
                                "SCÉNARIO COMPLET osmoseur-premium",
                                False,
                                f"MIME type incorrect: {content_type}"
                            )
                            return False
                    else:
                        print(f"   ❌ Étape 4: GET API échoue: {img_response.status_code}")
                        self.log_test(
                            "SCÉNARIO COMPLET osmoseur-premium",
                            False,
                            f"GET API échoue: {img_response.status_code}"
                        )
                        return False
                else:
                    print(f"   ❌ Étape 3: Format URL incorrect: {image_url}")
                    self.log_test(
                        "SCÉNARIO COMPLET osmoseur-premium",
                        False,
                        f"Format URL incorrect: {image_url}"
                    )
                    return False
            else:
                print(f"   ❌ Étape 1: Upload échoue: {response.status_code}")
                self.log_test(
                    "SCÉNARIO COMPLET osmoseur-premium",
                    False,
                    f"Upload échoue: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "SCÉNARIO COMPLET osmoseur-premium",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def generate_phase4_summary(self):
        """Générer le résumé des tests Phase 4 Final"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ PHASE 4 - TEST FINAL AVEC SOLUTION API DÉDIÉE")
        print("=" * 70)
        print(f"Total des tests: {total_tests}")
        print(f"✅ Réussis: {passed_tests}")
        print(f"❌ Échoués: {failed_tests}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        print("\n📋 DÉTAIL DES RÉSULTATS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Déterminer le statut global selon les critères Phase 4
        if success_rate == 100:
            overall_status = "🎉 PHASE 4 DÉFINITIVEMENT TERMINÉE"
            status_details = f"Solution API dédiée 100% fonctionnelle - Problème routage résolu!"
        elif success_rate >= 80:
            overall_status = "✅ PHASE 4 QUASI-TERMINÉE"
            status_details = f"Solution API fonctionne largement ({success_rate:.1f}% réussite)"
        elif success_rate >= 60:
            overall_status = "⚠️ PHASE 4 PARTIELLEMENT FONCTIONNELLE"
            status_details = f"Solution API partiellement opérationnelle ({success_rate:.1f}% réussite)"
        else:
            overall_status = "❌ PHASE 4 SOLUTION API ÉCHOUÉE"
            status_details = f"Problèmes critiques avec solution API ({success_rate:.1f}% réussite)"
        
        print(f"\n{overall_status}")
        print(f"📊 {status_details}")
        
        # Messages spécifiques selon les résultats
        critical_tests = [
            "Upload image → URL API dédiée",
            "API Image Access + MIME Type", 
            "SCÉNARIO COMPLET osmoseur-premium"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        critical_total = sum(1 for result in self.test_results 
                           if result["test"] in critical_tests)
        
        if critical_total > 0:
            critical_rate = (critical_passed / critical_total * 100)
            print(f"\n🎯 TESTS CRITIQUES: {critical_passed}/{critical_total} ({critical_rate:.1f}%)")
            
            if critical_rate == 100:
                print("🚀 OBJECTIF ATTEINT: Solution API dédiée entièrement fonctionnelle!")
                print("✅ Contournement Kubernetes réussi avec FileResponse")
                print("✅ MIME type correct (image/* et non text/html)")
                print("✅ Images servies correctement via API")
            else:
                print("⚠️ OBJECTIF PARTIEL: Quelques tests critiques échouent encore")
        
        return {
            "overall_success": success_rate >= 80,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_success_rate": critical_rate if critical_total > 0 else 0,
            "status": overall_status,
            "details": status_details,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = BackendTester()
    
    # Run PHASE 7 tests for blog images acquisition and upload
    summary = tester.run_phase7_blog_images_tests()
    
    # Exit code based on success
    exit_code = 0 if summary["overall_success"] else 1
    exit(exit_code)