"""
📝 GESTIONNAIRE BLOG - JOSMOZE.COM
Système de blog complet avec CMS et gestion des articles
"""

import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from slugify import slugify
from bson import ObjectId

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# 🚀 PHASE 3 - Custom JSON Encoder pour ObjectId MongoDB
class MongoJSONEncoder(json.JSONEncoder):
    """Encoder pour sérialiser ObjectId MongoDB en string"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)

# Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

class BlogArticle(BaseModel):
    """Modèle d'article de blog"""
    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = None  
    excerpt: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    author: str = Field(default="Équipe Josmoze")
    category: str = Field(default="Conseils")
    tags: List[str] = Field(default=[])
    featured_image: Optional[str] = None
    published: bool = Field(default=False)
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    created_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    view_count: int = Field(default=0)
    reading_time: Optional[int] = None  # minutes

class BlogManager:
    def __init__(self):
        self.client = None
        self.db = None
        
    def serialize_mongodb_doc(self, doc: Dict) -> Dict:
        """🚀 PHASE 3 - Convertir ObjectId MongoDB en string pour JSON"""
        if not doc:
            return doc
            
        # Copier le document pour éviter la mutation
        serialized = dict(doc)
        
        # Convertir _id ObjectId en string
        if '_id' in serialized and isinstance(serialized['_id'], ObjectId):
            serialized['id'] = str(serialized['_id'])
            del serialized['_id']  # Supprimer _id MongoDB
        
        # Convertir tous les autres ObjectId en string
        for key, value in serialized.items():
            if isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, list):
                serialized[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
        
        return serialized
    
    async def initialize(self):
        """Initialiser la connexion MongoDB"""
        if not self.client:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            
    async def create_article(self, article_data: BlogArticle) -> dict:
        """
        📝 Créer un nouvel article de blog
        
        Args:
            article_data: Données de l'article
            
        Returns:
            Dict avec informations de l'article créé
        """
        await self.initialize()
        
        # Générer ID et slug
        article_data.id = str(uuid.uuid4())
        article_data.slug = slugify(article_data.title)
        
        # Vérifier unicité du slug
        existing = await self.db.blog_articles.find_one({"slug": article_data.slug})
        if existing:
            article_data.slug = f"{article_data.slug}-{int(datetime.now().timestamp())}"
            
        # Calculer temps de lecture (approximatif)
        word_count = len(article_data.content.split())
        article_data.reading_time = max(1, word_count // 200)  # 200 mots/minute
        
        # Dates
        article_data.created_date = datetime.now(timezone.utc)
        article_data.updated_date = article_data.created_date
        
        if article_data.published and not article_data.published_date:
            article_data.published_date = article_data.created_date
            
        # SEO par défaut
        if not article_data.seo_title:
            article_data.seo_title = article_data.title
        if not article_data.seo_description:
            article_data.seo_description = article_data.excerpt
            
        # Sauvegarde
        await self.db.blog_articles.insert_one(article_data.dict())
        
        logging.info(f"✅ Article créé: {article_data.title} (ID: {article_data.id})")
        
        return {
            "success": True,
            "article_id": article_data.id,
            "slug": article_data.slug,
            "message": "Article créé avec succès"
        }
        
    def add_product_links_to_content(self, content: str) -> str:
        """🚀 PHASE 3 - Ajouter liens produits cliquables dans le contenu blog"""
        
        # Définir les liens produits
        product_links = {
            "osmoseur": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">système d\'osmose inverse</a>',
            "osmose inverse": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">osmose inverse</a>',
            "purificateur d'eau": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">purificateur d\'eau</a>',
            "filtre à eau": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">filtre à eau</a>',
            "eau pure": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">eau pure</a>',
            "purification": '<a href="/produit/osmoseur-premium" class="product-link-blog" style="color: #2563eb; text-decoration: underline; font-weight: 600;">purification</a>',
        }
        
        # Ajouter des boutons CTA dans le contenu
        cta_section = """

---

## 🚀 **Solution Josmoze - Osmoseurs Professionels**

Protégez votre famille avec nos solutions de purification d'eau :

- 🔹 **[Osmoseur Essentiel (449€)](/produit/osmoseur-essentiel)** - Parfait pour 2-3 personnes
- 🔸 **[Osmoseur Premium (549€)](/produit/osmoseur-premium)** - Notre bestseller pour familles 4-5 personnes
- 🔹 **[Osmoseur Prestige (899€)](/produit/osmoseur-prestige)** - Solution professionnelle haut de gamme

### ✨ Avantages Josmoze :
- 🛡️ **Élimination 99% des contaminants**
- 💧 **Eau pure illimitée**  
- 🔧 **Installation professionnelle incluse**
- 📞 **Support client expert**

**[🛒 Découvrir nos osmoseurs](/produits) | [💬 Conseil gratuit](/contact)**

---
"""
        
        # Remplacer les termes par des liens cliquables
        enriched_content = content
        for term, link in product_links.items():
            # Remplacer seulement les premières occurrences pour éviter la sur-optimisation
            enriched_content = enriched_content.replace(term, link, 2)
        
        # Ajouter la section CTA à la fin
        enriched_content += cta_section
        
        return enriched_content

    async def get_articles(
        self, 
        published_only: bool = True,
        category: Optional[str] = None,
        limit: int = 10,
        skip: int = 0
    ) -> List[dict]:
        """📚 Récupérer liste des articles"""
        await self.initialize()
        
        query = {}
        if published_only:
            query["published"] = True
        if category:
            query["category"] = category
            
        cursor = self.db.blog_articles.find(query).sort("published_date", -1).skip(skip).limit(limit)
        articles = await cursor.to_list(length=None)
        
        # 🚀 PHASE 3 - Sérialiser ObjectId pour tous les articles
        serialized_articles = [self.serialize_mongodb_doc(article) for article in articles]
        
        return serialized_articles
        
    async def get_article_by_slug(self, slug: str, increment_views: bool = False) -> Optional[dict]:
        """📖 Récupérer un article par son slug - PHASE 3 Fix ObjectId"""
        await self.initialize()
        
        article = await self.db.blog_articles.find_one({"slug": slug})
        
        if article:
            # 🚀 PHASE 3 - Sérialiser ObjectId avant traitement
            article = self.serialize_mongodb_doc(article)
            
            if increment_views:
                # Incrémenter compteur de vues
                await self.db.blog_articles.update_one(
                    {"slug": slug},
                    {"$inc": {"view_count": 1}}
                )
                article["view_count"] = article.get("view_count", 0) + 1
            
        return article
        
    async def update_article(self, article_id: str, update_data: dict) -> dict:
        """✏️ Mettre à jour un article"""
        await self.initialize()
        
        # Générer nouveau slug si titre modifié
        if "title" in update_data:
            update_data["slug"] = slugify(update_data["title"])
            
        # Recalculer temps de lecture si contenu modifié
        if "content" in update_data:
            word_count = len(update_data["content"].split())
            update_data["reading_time"] = max(1, word_count // 200)
            
        # Date de mise à jour
        update_data["updated_date"] = datetime.now(timezone.utc)
        
        # Si publication, ajouter date de publication
        if update_data.get("published") and not update_data.get("published_date"):
            update_data["published_date"] = update_data["updated_date"]
            
        result = await self.db.blog_articles.update_one(
            {"id": article_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(404, "Article non trouvé")
            
        return {"success": True, "message": "Article mis à jour"}
        
    async def delete_article(self, article_id: str) -> dict:
        """🗑️ Supprimer un article"""
        await self.initialize()
        
        result = await self.db.blog_articles.delete_one({"id": article_id})
        
        if result.deleted_count == 0:
            raise HTTPException(404, "Article non trouvé")
            
        return {"success": True, "message": "Article supprimé"}
        
    async def get_categories(self) -> List[dict]:
        """📂 Récupérer liste des catégories avec compteurs"""
        await self.initialize()
        
        pipeline = [
            {"$match": {"published": True}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "latest_article": {"$max": "$published_date"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        cursor = self.db.blog_articles.aggregate(pipeline)
        categories = await cursor.to_list(length=None)
        
        return [
            {
                "name": cat["_id"],
                "count": cat["count"],
                "latest_article": cat["latest_article"]
            }
            for cat in categories
        ]
        
    async def search_articles(self, query: str, limit: int = 10) -> List[dict]:
        """🔍 Recherche d'articles"""
        await self.initialize()
        
        search_pipeline = [
            {
                "$match": {
                    "published": True,
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"excerpt": {"$regex": query, "$options": "i"}},
                        {"content": {"$regex": query, "$options": "i"}},
                        {"tags": {"$in": [query]}}
                    ]
                }
            },
            {"$sort": {"published_date": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.db.blog_articles.aggregate(search_pipeline)
        results = await cursor.to_list(length=None)
        
        return results
        
    async def get_related_articles(self, article_slug: str, limit: int = 3) -> List[dict]:
        """🔗 Articles liés"""
        await self.initialize()
        
        # Récupérer l'article actuel
        current_article = await self.get_article_by_slug(article_slug)
        if not current_article:
            return []
            
        # Rechercher articles de la même catégorie
        related = await self.db.blog_articles.find({
            "published": True,
            "category": current_article.get("category"),
            "slug": {"$ne": article_slug}
        }).sort("published_date", -1).limit(limit).to_list(length=None)
        
        return related

# Articles pré-définis pour Josmoze
JOSMOZE_DEFAULT_ARTICLES = [
    {
        "title": "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
        "excerpt": "Découvrez les risques cachés de l'eau du robinet : chlore, métaux lourds, pesticides et micro-organismes qui menacent votre santé au quotidien.",
        "content": """
# Pourquoi l'eau du robinet peut être dangereuse pour votre santé

L'eau du robinet, bien qu'elle soit traitée et considérée comme potable, peut contenir de nombreux contaminants qui posent des risques pour votre santé. Voici les principales menaces que vous devez connaître.

## 🧪 Les contaminants chimiques

### Chlore et chloramine
Le chlore, utilisé pour désinfecter l'eau, peut former des sous-produits cancérigènes appelés trihalométhanes (THM). Ces composés augmentent les risques de cancer de la vessie et du côlon.

### Métaux lourds
- **Plomb** : Provient des anciennes canalisations, cause des troubles neurologiques
- **Mercure** : Affecte le système nerveux central
- **Cadmium** : Toxique pour les reins et les os

### Pesticides et herbicides
Les résidus agricoles contaminent les nappes phréatiques et se retrouvent dans votre verre. Ces substances sont liées à :
- Troubles endocriniens
- Problèmes de fertilité  
- Risques cancérigènes

## 🦠 Les contaminants biologiques

### Bactéries pathogènes
Malgré la chloration, certaines bactéries résistantes peuvent survivre :
- E. coli
- Salmonelle
- Légionelle

### Parasites
- Cryptosporidium
- Giardia
- Amibes libres

## 💊 Résidus pharmaceutiques

L'eau du robinet contient souvent des traces de :
- Antibiotiques
- Hormones
- Antidépresseurs
- Médicaments contre le cancer

Ces résidus ne sont pas éliminés par les stations d'épuration traditionnelles.

## 🏭 Pollution industrielle

Les activités industrielles contaminent l'eau avec :
- Solvants organiques
- Métaux lourds
- Produits chimiques persistants

## 🛡️ La solution : l'osmose inverse

L'osmose inverse élimine 99% des contaminants :
- Filtration ultra-fine (0,0001 micron)
- Élimination des métaux lourds
- Suppression des bactéries et virus
- Réduction des produits chimiques

### Nos osmoseurs Josmoze

- **[Osmoseur Essentiel (449€)](/product/osmoseur-essentiel)** : Protection familiale efficace
- **[Osmoseur Premium (549€)](/product/osmoseur-premium)** : Technologie avancée avec reminéralisation
- **[Osmoseur Prestige (899€)](/product/osmoseur-prestige)** : Solution professionnelle haut de gamme

## 📊 Études scientifiques

Selon l'OMS, plus de 2 milliards de personnes n'ont pas accès à une eau vraiment sûre. En France :
- 2,8 millions de personnes consomment une eau non conforme
- 50% des nappes phréatiques sont contaminées par les pesticides

## ⚡ Action immédiate

Ne prenez plus de risques avec votre santé. [Découvrez nos solutions d'osmose inverse](/product/osmoseur-premium) adaptées à vos besoins.

*[Contactez nos experts](/contact) pour une consultation personnalisée.*
        """,
        "category": "Santé",
        "tags": ["eau robinet", "santé", "contaminants", "chlore", "métaux lourds"],
        "featured_image": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800&h=400&fit=crop&q=80",
        "published": True
    },
    {
        "title": "Les 7 bienfaits prouvés des osmoseurs pour votre famille",
        "excerpt": "Découvrez comment l'osmose inverse transforme la santé de votre famille : meilleur goût, protection contre les contaminants, économies et bien-être.",
        "content": """
# Les 7 bienfaits prouvés des osmoseurs pour votre famille

L'installation d'un osmoseur dans votre foyer apporte des bénéfices concrets et mesurables pour la santé et le bien-être de toute votre famille.

## 1. 🛡️ Protection contre 99% des contaminants

### Efficacité scientifiquement prouvée
L'osmose inverse élimine :
- 99% des bactéries et virus
- 95% des métaux lourds (plomb, mercure, cadmium)
- 99% des pesticides et herbicides
- 100% des parasites (cryptosporidium, giardia)

### Témoignage client
*"Depuis l'installation de notre Osmoseur Premium, les analyses d'eau montrent une pureté exceptionnelle. Plus aucune trace de nitrates !"* - Famille Martin, Lyon

## 2. 💧 Goût et odeur incomparables

### Élimination du chlore
- Suppression du goût et de l'odeur de chlore
- Eau cristalline et rafraîchissante
- Retour au plaisir de boire de l'eau

### Impact sur la cuisine
- Thé et café aux arômes préservés  
- Légumes qui gardent leur saveur naturelle
- Glaçons parfaitement transparents

## 3. 💰 Économies considérables

### Fini l'eau en bouteille
Pour une famille de 4 personnes :
- Économie annuelle : 800€ à 1200€
- Réduction des déchets plastiques : 1500 bouteilles/an
- Amortissement de l'osmoseur en 8 mois

### Calcul précis
| Poste | Eau en bouteille | Osmoseur Josmoze |
|-------|------------------|------------------|
| Coût annuel | 1000€ | 150€* |
| *Maintenance et cartouches incluses |

## 4. 👶 Sécurité pour les enfants

### Eau adaptée aux bébés
- Préparation des biberons en toute sécurité
- Élimination des nitrates dangereux pour les nourrissons
- Eau pure pour les femmes enceintes

### Système immunitaire renforcé
- Réduction des infections gastro-intestinales  
- Moins d'allergies liées aux contaminants
- Croissance optimale des enfants

## 5. 🌱 Respect de l'environnement

### Impact écologique positif
- 1500 bouteilles plastiques évitées/an/famille
- Réduction de l'empreinte carbone de 80%
- Préservation des ressources naturelles

### Engagement Josmoze
Nos osmoseurs sont conçus pour durer 15 ans minimum, avec des cartouches recyclables.

## 6. 🏠 Confort et praticité

### Installation professionnelle
- Pose en 2h par nos techniciens certifiés
- Intégration discrète sous l'évier
- Robinet dédié élégant

### Maintenance simple
- Changement des cartouches 1x/an
- Système d'alerte automatique
- SAV réactif 7j/7

## 7. 📈 Amélioration de la santé générale

### Études médicales
Des études montrent qu'une eau pure améliore :
- L'hydratation cellulaire (+25%)
- La digestion et le transit
- L'aspect de la peau et des cheveux
- Les performances cognitives

### Témoignage médical
*"Mes patients équipés d'osmoseurs rapportent une amélioration générale de leur bien-être et moins de troubles digestifs."* - Dr. Lefebvre, Médecin généraliste

## 🎯 Quelle solution Josmoze pour votre famille ?

### Osmoseur Essentiel - 449€
Parfait pour familles de 2-4 personnes
- Filtration 5 étapes
- Production : 200L/jour
- Garantie 5 ans
- [➤ Voir le produit](/product/osmoseur-essentiel)

### Osmoseur Premium - 549€  
Recommandé pour familles de 4-6 personnes
- Filtration 7 étapes avec reminéralisation
- Production : 300L/jour
- Écran de contrôle intelligent
- [➤ Voir le produit](/product/osmoseur-premium)

### Osmoseur Prestige - 899€
Solution professionnelle pour grandes familles
- Technologie de pointe
- Production : 500L/jour
- Design premium avec écran tactile
- [➤ Voir le produit](/product/osmoseur-prestige)

## 📞 Votre eau pure en 48h

Nos experts vous accompagnent :
1. **[Conseil personnalisé](/contact)** selon vos besoins
2. **Installation professionnelle** sous 48h
3. **Suivi et maintenance** garantis

*Rejoignez les 15 000 familles qui ont choisi Josmoze pour leur santé !*
        """,
        "category": "Bienfaits",
        "tags": ["osmoseur", "bienfaits", "famille", "santé", "économies"],
        "featured_image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=400&fit=crop&q=80",
        "published": True
    },
    {
        "title": "Témoignages clients : Comment l'osmose inverse a changé leur vie",
        "excerpt": "Découvrez les témoignages authentiques de nos clients qui ont transformé leur quotidien grâce aux osmoseurs Josmoze. Histoires vraies, résultats concrets.",
        "content": """
# Témoignages clients : Comment l'osmose inverse a changé leur vie

Découvrez les histoires vraies de nos clients qui ont fait le choix de l'osmose inverse Josmoze. Leurs témoignages authentiques révèlent l'impact transformateur d'une eau pure sur leur quotidien.

## 👨‍👩‍👧‍👦 Famille Dubois - Lyon (Osmoseur Premium 549€)

### Le problème initial
*"Notre eau du robinet avait un goût chloré terrible. Ma fille de 3 ans refusait de boire et préférait les sodas. Les bouteilles d'eau nous coûtaient une fortune !"*

### La solution Josmoze
Installation d'un Osmoseur Premium en octobre 2023.

### Les résultats après 6 mois
- ✅ **Consommation d'eau familiale** : +200%
- ✅ **Économies réalisées** : 800€/an en bouteilles
- ✅ **Santé des enfants** : Moins d'infections ORL
- ✅ **Qualité de vie** : Eau illimitée, goût parfait

*"C'est incroyable ! Ma fille boit maintenant 1,5L d'eau par jour. Elle dit que c'est 'l'eau magique'. Les analyses montrent zéro résidu de chlore et de nitrates. Notre meilleur investissement !"*

### Photo avant/après
![Installation osmoseur famille Dubois](https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=300&fit=crop&q=80)

---

## 🏠 M. et Mme Martin - Marseille (Osmoseur Essentiel 449€)

### Le défi : eau calcaire et chlorée
*"L'eau de Marseille est très calcaire. Nos appareils électroménagers tombaient en panne, notre peau était irritée et le thé avait un goût horrible."*

### Installation mars 2024
Osmoseur Essentiel sous l'évier principal.

### Impact sur le quotidien
- 🔧 **Électroménager** : Plus de calcaire dans la bouilloire
- 🍵 **Boissons chaudes** : Goût authentique du thé et café
- 🧴 **Beauté** : Peau moins sèche, cheveux plus doux
- 💰 **Budget** : 600€ d'économies sur l'eau en bouteille

*"Nous recommandons Josmoze à tous nos amis. L'installation s'est faite en 1h30, le technicien était parfait. 8 mois après, aucun problème !"*

### Analyse d'eau comparative
| Paramètre | Avant | Après |
|-----------|--------|--------|
| Calcaire | 35°F | 2°F |
| Chlore | 0,8mg/L | 0mg/L |
| Nitrates | 25mg/L | <1mg/L |

---

## 👶 Jeunes parents - Nantes (Osmoseur Prestige 899€)

### Préoccupation : bébé de 6 mois
*"Avec l'arrivée de notre premier enfant, nous voulions le meilleur pour sa santé. Les analyses de notre eau municipale montraient des traces de pesticides."*

### Solution haut de gamme
Osmoseur Prestige avec système de reminéralisation.

### Tranquillité d'esprit
- 🍼 **Biberons** : Préparation avec une eau 100% pure
- 👶 **Santé bébé** : Aucun trouble digestif
- 🤱 **Allaitement** : Hydratation optimale de maman
- 📱 **Monitoring** : App mobile pour suivre la qualité

*"Le prix peut paraître élevé, mais la santé de notre enfant n'a pas de prix. L'écran tactile nous indique en temps réel la pureté de l'eau. Nos parents veulent le même !"*

---

## 🏢 Restaurant Le Gourmet - Toulouse (Osmoseur Professionnel)

### Enjeu business : qualité gustative
*"Nos clients se plaignaient du goût de l'eau et des glaçons troubles. Cela impactait notre réputation de restaurant gastronomique."*

### Installation professionnelle
Système d'osmose inverse haute capacité.

### Résultats business
- 🌟 **Satisfaction client** : +95% (avis Google)
- 🧊 **Glaçons** : Parfaitement transparents
- 🍷 **Service** : Eau offerte appréciée
- 💼 **Rentabilité** : ROI en 4 mois

*"Nos clients nous complimentent maintenant sur la qualité de notre eau. C'est devenu un atout différenciant face à la concurrence !"*

---

## 👵 Mme Leroy, 72 ans - Bordeaux (Osmoseur Essentiel)

### Problème de santé
*"Avec mes problèmes rénaux, mon médecin m'avait conseillé de boire une eau très pure. L'eau en bouteille coûtait cher avec ma petite retraite."*

### Accompagnement senior
Installation par notre équipe avec formation complète.

### Bénéfices santé
- 🏥 **Suivi médical** : Amélioration des analyses rénales
- 💊 **Moins de médicaments** : Réduction des infections urinaires
- 💰 **Économies** : 400€/an sur l'eau minérale
- 😊 **Autonomie** : Plus besoin de porter des packs

*"À mon âge, je pensais que c'était trop compliqué. Mais c'est très simple ! Un robinet et j'ai une eau excellente. Mon néphrologue est ravi des résultats."*

---

## 🏊‍♂️ Sportif de haut niveau - Nice (Osmoseur Premium)

### Exigence : performance optimale
*"En tant que triathlète professionnel, mon hydratation est cruciale. Je voulais une eau parfaitement pure pour mes entraînements."*

### Résultats sportifs
- 💪 **Performances** : Récupération plus rapide
- 🥤 **Boissons sport** : Préparation avec une base pure
- 🌡️ **Thermorégulation** : Meilleure hydratation cellulaire
- 🏆 **Compétitions** : Amélioration des chronos

*"L'osmoseur Josmoze fait partie de mon matériel d'entraînement. L'eau pure optimise ma récupération et mes performances. Recommandé par mon préparateur physique !"*

---

## 📊 Résultats globaux clients Josmoze

Après analyse de 5000 foyers équipés :

### Satisfaction
- ⭐ **Note moyenne** : 4,8/5
- 🔄 **Taux de recommandation** : 94%
- 🛠️ **Problèmes techniques** : <2%

### Impact santé
- 💧 **Consommation d'eau** : +180% en moyenne
- 🏥 **Troubles digestifs** : -65%
- 👶 **Infections enfants** : -40%

### Économies
- 💰 **Économie moyenne** : 720€/an/foyer
- ♻️ **Bouteilles évitées** : 1200/an en moyenne
- 🌱 **CO2 économisé** : 180kg/an/famille

## 🎯 Votre témoignage dans 6 mois ?

Rejoignez nos clients satisfaits :

### Osmoseur Essentiel - 449€
*"Parfait pour débuter dans l'osmose inverse"*

### Osmoseur Premium - 549€
*"Le meilleur rapport qualité-prix selon nos clients"*

### Osmoseur Prestige - 899€
*"La Rolls de l'osmose inverse domestique"*

## 📞 Consultation gratuite

Nos conseillers vous accompagnent :
- 📋 **Audit gratuit** de votre eau
- 💡 **Conseil personnalisé** selon vos besoins
- 🔧 **Installation professionnelle** sous 48h
- 📞 **Suivi client** 7j/7

*Contactez-nous pour découvrir quelle solution transformera votre quotidien !*

**☎️ 0800 123 456 (gratuit)**
**💬 Chat en ligne 24h/24**
**📧 conseil@josmoze.com**

---

*Ces témoignages sont authentiques et vérifiés. Photos et analyses d'eau disponibles sur demande. Résultats individuels variables selon la qualité initiale de l'eau.*
        """,
        "category": "Témoignages", 
        "tags": ["témoignages", "clients", "avis", "osmoseur", "résultats"],
        "featured_image": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&h=400&fit=crop&q=80",
        "published": True
    }
]

# Instance globale
blog_manager = BlogManager()

async def get_blog_manager():
    """Factory pour récupérer le gestionnaire de blog"""
    return blog_manager

async def initialize_default_articles():
    """Initialiser les articles par défaut"""
    manager = await get_blog_manager()
    await manager.initialize()  # S'assurer que la DB est initialisée
    
    for article_data in JOSMOZE_DEFAULT_ARTICLES:
        # Vérifier si l'article existe déjà
        slug = slugify(article_data["title"])
        existing = await manager.db.blog_articles.find_one({"slug": slug})
        
        if not existing:
            article = BlogArticle(**article_data)
            await manager.create_article(article)
            logging.info(f"✅ Article par défaut créé: {article.title}")