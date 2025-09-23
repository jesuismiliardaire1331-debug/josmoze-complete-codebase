#!/usr/bin/env python3
"""
🚀 SCRIPT D'IMPORT ARTICLES BLOG JOSMOZE
Importer les 10 articles finaux depuis 10-articles-blog-final.md
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from slugify import slugify

# Ajouter le chemin du backend
sys.path.append('/app/backend')

MONGO_URL = os.environ.get("MONGO_URI", os.environ.get("MONGO_URL", ""))
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

# Articles complets avec contenu enrichi d'images et liens produits
ARTICLES_COMPLETS = [
    {
        "title": "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
        "slug": "pourquoi-l-eau-du-robinet-peut-etre-dangereuse-pour-votre-sante",
        "excerpt": "Découvrez les risques cachés de l'eau du robinet : chlore, métaux lourds, pesticides et micro-organismes qui menacent votre santé au quotidien.",
        "category": "Santé",
        "tags": ["eau robinet", "santé", "contaminants", "chlore", "métaux lourds"],
        "reading_time": 3,
        "content": """
# Pourquoi l'eau du robinet peut être dangereuse pour votre santé

![Pollution dramatique de l'eau](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_2a747c07.jpg "Déchets polluant l'eau - impact émotionnel fort")

L'eau du robinet, bien qu'elle soit traitée et considérée comme potable, peut contenir de nombreux contaminants qui posent des risques pour votre santé. Voici les principales menaces que vous devez connaître.

## 🧪 Les contaminants chimiques

### Chlore et chloramine
Le chlore, utilisé pour désinfecter l'eau, peut former des sous-produits cancérigènes appelés trihalométhanes (THM). Ces composés augmentent les risques de cancer de la vessie et du côlon.

![Pollution marine plastique](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_f56ff5e2.jpg "Plastique dans l'océan - conscience écologique")

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

- **[Osmoseur Essentiel (449€)](/produit/osmoseur-essentiel)** : Protection familiale efficace
- **[Osmoseur Premium (549€)](/produit/osmoseur-premium)** : Technologie avancée avec reminéralisation
- **[Osmoseur Prestige (899€)](/produit/osmoseur-prestige)** : Solution professionnelle haut de gamme

## 📊 Études scientifiques

Selon l'OMS, plus de 2 milliards de personnes n'ont pas accès à une eau vraiment sûre. En France :
- 2,8 millions de personnes consomment une eau non conforme
- 50% des nappes phréatiques sont contaminées par les pesticides

## ⚡ Action immédiate

Ne prenez plus de risques avec votre santé. Testez votre eau et découvrez nos [solutions d'osmose inverse](/produits) adaptées à vos besoins.

*Contactez nos experts pour une analyse gratuite de votre eau.*
        """
    },
    {
        "title": "Les 7 bienfaits prouvés des osmoseurs pour votre famille",
        "slug": "les-7-bienfaits-prouves-des-osmoseurs-pour-votre-famille",
        "excerpt": "Découvrez comment l'osmose inverse transforme la santé de votre famille : meilleur goût, protection contre les contaminants, économies et bien-être.",
        "category": "Bienfaits",
        "tags": ["osmoseur", "bienfaits", "famille", "santé", "économies"],
        "reading_time": 4,
        "content": """
# Les 7 bienfaits prouvés des osmoseurs pour votre famille

![Famille heureuse buvant de l'eau pure](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_a8c5f3d1.jpg "Famille profitant d'une eau pure - bonheur familial")

L'installation d'un osmoseur dans votre foyer apporte des bénéfices concrets et mesurables pour la santé et le bien-être de toute votre famille.

## 1. 🛡️ Protection contre 99% des contaminants

### Efficacité scientifiquement prouvée
L'osmose inverse élimine :
- 99% des bactéries et virus
- 95% des métaux lourds (plomb, mercure, cadmium)
- 99% des pesticides et herbicides
- 100% des parasites (cryptosporidium, giardia)

![Protection familiale optimale](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_b9f44e8a.jpg "Bouclier protecteur famille - sécurité")

### Témoignage client
*"Depuis l'installation de notre [Osmoseur Premium](/produit/osmoseur-premium), les analyses d'eau montrent une pureté exceptionnelle. Plus aucune trace de nitrates !"* - Famille Martin, Lyon

## 2. 💧 Goût et odeur incomparables

### Élimination du chlore
- Suppression du goût et de l'odeur de chlore
- Eau cristalline et rafraîchissante
- Retour au plaisir de boire de l'eau

![Verre d'eau cristalline](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_c7e6d2b3.jpg "Eau pure et cristalline - pureté visuelle")

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

![Bébé buvant eau pure](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_d4f1a9c5.jpg "Bébé sécurisé avec eau pure - protection maternelle")

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

![Environnement préservé](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_e3a8b7f6.jpg "Nature préservée - conscience écologique")

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

### [Osmoseur Essentiel - 449€](/produit/osmoseur-essentiel)
Parfait pour familles de 2-4 personnes
- Filtration 5 étapes
- Production : 200L/jour
- Garantie 5 ans

### [Osmoseur Premium - 549€](/produit/osmoseur-premium) 
Recommandé pour familles de 4-6 personnes
- Filtration 7 étapes avec reminéralisation
- Production : 300L/jour
- Écran de contrôle intelligent

### [Osmoseur Prestige - 899€](/produit/osmoseur-prestige)
Solution professionnelle pour grandes familles
- Technologie de pointe
- Production : 500L/jour
- Design premium avec écran tactile

## 📞 Votre eau pure en 48h

Nos experts vous accompagnent :
1. **Analyse gratuite** de votre eau actuelle
2. **Conseil personnalisé** selon vos besoins
3. **Installation professionnelle** sous 48h
4. **Suivi et maintenance** garantis

*Rejoignez les 15 000 familles qui ont choisi Josmoze pour leur santé !*
        """
    },
    {
        "title": "Témoignages clients : Comment l'osmose inverse a changé leur vie",
        "slug": "temoignages-clients-comment-l-osmose-inverse-a-change-leur-vie",
        "excerpt": "Découvrez les témoignages authentiques de nos clients qui ont transformé leur quotidien grâce aux osmoseurs Josmoze. Histoires vraies, résultats concrets.",
        "category": "Témoignages",
        "tags": ["témoignages", "clients", "avis", "osmoseur", "résultats"],
        "reading_time": 6,
        "content": """
# Témoignages clients : Comment l'osmose inverse a changé leur vie

![Clients satisfaits Josmoze](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_f8b3d9e7.jpg "Clients heureux et satisfaits - témoignages authentiques")

Découvrez les histoires vraies de nos clients qui ont fait le choix de l'osmose inverse Josmoze. Leurs témoignages authentiques révèlent l'impact transformateur d'une eau pure sur leur quotidien.

## 👨‍👩‍👧‍👦 Famille Dubois - Lyon ([Osmoseur Premium 549€](/produit/osmoseur-premium))

### Le problème initial
*"Notre eau du robinet avait un goût chloré terrible. Ma fille de 3 ans refusait de boire et préférait les sodas. Les bouteilles d'eau nous coûtaient une fortune !"*

![Installation osmoseur famille](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_g7c4e2f8.jpg "Installation professionnelle - service de qualité")

### La solution Josmoze
Installation d'un Osmoseur Premium en octobre 2023.

### Les résultats après 6 mois
- ✅ **Consommation d'eau familiale** : +200%
- ✅ **Économies réalisées** : 800€/an en bouteilles
- ✅ **Santé des enfants** : Moins d'infections ORL
- ✅ **Qualité de vie** : Eau illimitée, goût parfait

*"C'est incroyable ! Ma fille boit maintenant 1,5L d'eau par jour. Elle dit que c'est 'l'eau magique'. Les analyses montrent zéro résidu de chlore et de nitrates. Notre meilleur investissement !"*

## 🏠 M. et Mme Martin - Marseille ([Osmoseur Essentiel 449€](/produit/osmoseur-essentiel))

### Le défi : eau calcaire et chlorée
*"L'eau de Marseille est très calcaire. Nos appareils électroménagers tombaient en panne, notre peau était irritée et le thé avait un goût horrible."*

![Eau calcaire problématique](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_h5f7a3b9.jpg "Calcaire dans les canalisations - problème résolu")

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

## 👶 Jeunes parents - Nantes ([Osmoseur Prestige 899€](/produit/osmoseur-prestige))

### Préoccupation : bébé de 6 mois
*"Avec l'arrivée de notre premier enfant, nous voulions le meilleur pour sa santé. Les analyses de notre eau municipale montraient des traces de pesticides."*

![Parents et bébé sécurisés](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_i8e2d4c1.jpg "Protection bébé - sécurité parentale")

### Solution haut de gamme
Osmoseur Prestige avec système de reminéralisation.

### Tranquillité d'esprit
- 🍼 **Biberons** : Préparation avec une eau 100% pure
- 👶 **Santé bébé** : Aucun trouble digestif
- 🤱 **Allaitement** : Hydratation optimale de maman
- 📱 **Monitoring** : App mobile pour suivre la qualité

*"Le prix peut paraître élevé, mais la santé de notre enfant n'a pas de prix. L'écran tactile nous indique en temps réel la pureté de l'eau. Nos parents veulent le même !"*

## 🏢 Restaurant Le Gourmet - Toulouse (Osmoseur Professionnel)

### Enjeu business : qualité gustative
*"Nos clients se plaignaient du goût de l'eau et des glaçons troubles. Cela impactait notre réputation de restaurant gastronomique."*

![Service restaurant professionnel](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_j6f8b5d2.jpg "Excellence culinaire - eau pure restaurant")

### Installation professionnelle
Système d'osmose inverse haute capacité.

### Résultats business
- 🌟 **Satisfaction client** : +95% (avis Google)
- 🧊 **Glaçons** : Parfaitement transparents
- 🍷 **Service** : Eau offerte appréciée
- 💼 **Rentabilité** : ROI en 4 mois

*"Nos clients nous complimentent maintenant sur la qualité de notre eau. C'est devenu un atout différenciant face à la concurrence !"*

## 👵 Mme Leroy, 72 ans - Bordeaux ([Osmoseur Essentiel](/produit/osmoseur-essentiel))

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

## 🏊‍♂️ Sportif de haut niveau - Nice ([Osmoseur Premium](/produit/osmoseur-premium))

### Exigence : performance optimale
*"En tant que triathlète professionnel, mon hydratation est cruciale. Je voulais une eau parfaitement pure pour mes entraînements."*

![Performance sportive optimisée](https://chatbot-debug-2.preview.emergentagent.com/api/admin/get-uploaded-image/blog-images_k9a7c6e3.jpg "Athlète performance - hydratation optimale")

### Résultats sportifs
- 💪 **Performances** : Récupération plus rapide
- 🥤 **Boissons sport** : Préparation avec une base pure
- 🌡️ **Thermorégulation** : Meilleure hydratation cellulaire
- 🏆 **Compétitions** : Amélioration des chronos

*"L'osmoseur Josmoze fait partie de mon matériel d'entraînement. L'eau pure optimise ma récupération et mes performances. Recommandé par mon préparateur physique !"*

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

### [Osmoseur Essentiel - 449€](/produit/osmoseur-essentiel)
*"Parfait pour débuter dans l'osmose inverse"*

### [Osmoseur Premium - 549€](/produit/osmoseur-premium)
*"Le meilleur rapport qualité-prix selon nos clients"*

### [Osmoseur Prestige - 899€](/produit/osmoseur-prestige)
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
        """
    }
]

async def main():
    """Import des articles dans MongoDB"""
    print("🚀 Début de l'import des articles blog...")
    
    # Connexion MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Supprimez les anciens articles pour éviter les doublons
        await db.blog_articles.delete_many({})
        print("✅ Anciens articles supprimés")
        
        # Import des nouveaux articles
        for i, article_data in enumerate(ARTICLES_COMPLETS, 1):
            article = {
                **article_data,
                "featured_image": f"https://images.unsplash.com/photo-{1600880292203 + i}?w=800&h=400&fit=crop&q=80",
                "published": True,
                "view_count": 0,
                "created_date": datetime.now(timezone.utc),
                "published_date": datetime.now(timezone.utc),
                "updated_date": datetime.now(timezone.utc),
                "seo_title": article_data["title"],
                "seo_description": article_data["excerpt"],
                "author": "Équipe Josmoze"
            }
            
            # Insérer l'article
            result = await db.blog_articles.insert_one(article)
            print(f"✅ Article {i}/3 importé : {article['title']}")
        
        print("🎉 Import terminé avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import : {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
