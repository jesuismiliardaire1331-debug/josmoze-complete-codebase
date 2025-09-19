#!/usr/bin/env python3
"""
Produits finaux pour Josmoze.com - Version finale avec nouveaux produits et promotions
"""

FINAL_PRODUCTS = [
    # ======= GAMME OSMOSEURS RESTRUCTURÉE =======
    {
        "id": "osmoseur-essentiel",
        "name": "Osmoseur Essentiel - BlueMountain Compact",
        "description": "Solution d'entrée de gamme parfaite pour petits foyers. Osmose inverse professionnelle avec membrane 100GPD. Production 200L/jour. Installation simple sous évier.",
        "price": 449.0,
        "original_price": 549.0,
        "image": "https://images.unsplash.com/photo-1628239532623-c035054bff4e?w=800&h=800&fit=crop&q=80",
        "category": "osmoseur",
        "target_audience": "both",
        "product_tier": "essentiel",
        "specifications": {
            "Production d'eau": "Jusqu'à 200 litres/jour (8L/h)",
            "Membrane": "100GPD standard",
            "Filtration": "5 étapes de filtration",
            "Type": "Osmose Inverse (RO)",
            "Installation": "Sous évier - Simple",
            "Garantie": "2 ans",
            "Dimensions": "35×25×15 cm"
        },
        "features": [
            "Production jusqu'à 200 litres/jour (8 litres/heure)",
            "Membrane 100GPD performance standard",
            "5 étapes de filtration complète",
            "Installation sous évier facile",
            "Dimensions compactes: 35×25×15 cm",
            "Technologie BlueMountain fiable",
            "Support technique inclus",
            "Idéal foyers 1-3 personnes"
        ],
        "images_gallery": [
            "https://www.josmoze.com/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
            "https://www.josmoze.com/2566-small_default/fontaine-osmoseur-minibluesea.jpg"
        ],
        "in_stock": True
    },
    {
        "id": "osmoseur-premium",
        "name": "Osmoseur Premium - BlueMountain Avancé",
        "description": "Système d'osmose inverse avancé BlueMountain. Production 300L/jour (12L/h). Membrane 100GPD encapsulée. Eau chaude, froide et tempérée. Installation professionnelle incluse.",
        "price": 549.0,
        "original_price": 649.0,
        "image": "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png",
        "category": "osmoseur",
        "target_audience": "both",
        "product_tier": "premium",
        "promotion_eligible": True,
        "specifications": {
            "Production d'eau": "Jusqu'à 300 litres/jour (12L/h)",
            "Membrane": "100GPD encapsulée haute performance",
            "Filtration": "6 étapes de filtration avancée",
            "Type": "Osmose Inverse (RO) avec minéralisation",
            "Installation": "Professionnelle incluse",
            "Garantie": "3 ans pièces et main d'œuvre",
            "Températures": "Eau chaude, froide et tempérée"
        },
        "features": [
            "Production jusqu'à 300 litres/jour (12 litres/heure)",
            "Membrane 100GPD encapsulée haute performance",
            "6 étapes de filtration avec reminéralisation",
            "Eau chaude, froide et tempérée disponible",
            "Installation professionnelle par technicien",
            "Dimensions optimisées: 45×35×25 cm",
            "Technologie BlueMountain avancée",
            "Support technique prioritaire",
            "Idéal foyers 3-6 personnes"
        ],
        "images_gallery": [
            "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png",
            "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png"
        ],
        "in_stock": True
    },
    {
        "id": "osmoseur-prestige",
        "name": "Osmoseur Prestige - BlueMountain De Comptoir",
        "description": "Le nec plus ultra de l'osmose inverse ! Osmoseur de comptoir design avec contrôle digital intelligent. Production 380L/jour (16L/h). 7 étapes de filtration premium. Installation plug & play.",
        "price": 899.0,
        "original_price": 1199.0,
        "image": "https://www.josmoze.com/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
        "category": "osmoseur",
        "target_audience": "both",
        "product_tier": "prestige",
        "promotion_eligible": True,
        "specifications": {
            "Production d'eau": "Jusqu'à 380 litres/jour (16L/h)",
            "Membrane": "100GPD encapsulée premium",
            "Filtration": "7 étapes premium avec UV",
            "Type": "Osmose Inverse + UV + Reminéralisation",
            "Installation": "Plug & Play - De comptoir",
            "Garantie": "5 ans totale",
            "Contrôle": "Digital tactile intelligent",
            "Design": "Premium de comptoir"
        },
        "features": [
            "Production jusqu'à 380 litres/jour (16 litres/heure)",
            "Membrane 100GPD encapsulée premium",
            "7 étapes premium avec stérilisation UV",
            "Contrôle digital tactile intelligent",
            "Installation plug & play - aucun raccordement",
            "Design premium pour comptoir",
            "Réservoir intégré haute capacité",
            "Technologie BlueMountain premium",
            "Support VIP dédié",
            "Idéal familles nombreuses et bureaux"
        ],
        "images_gallery": [
            "https://www.josmoze.com/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
            "https://www.josmoze.com/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
            "https://www.josmoze.com/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png"
        ],
        "in_stock": True
    },
    
    # ======= NOUVEAUX PRODUITS =======
    {
        "id": "purificateur-portable-hydrogene",
        "name": "Purificateur Portable à Hydrogène H2-Pro",
        "description": "Révolutionnaire ! Purificateur portable qui enrichit l'eau en hydrogène moléculaire. Batterie 8h d'autonomie. Technologie SPE/PEM. Bouteille 420ml incluse. Antioxydant naturel puissant.",
        "price": 79.0,
        "original_price": 99.0,
        "image": "https://static.wixstatic.com/media/6af6bd_16baeaf62afc42009cf6ece2f46c767a~mv2.png/v1/fill/w_797,h_487,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Les%20b%C3%A9b%C3%A9s%20pleurent%20quand%20ils%20ont%20faim%2C%20ne%20peuvent%20pas%20attendre__%20c'est%20touj_20250220_19362.png",
        "category": "portable",
        "target_audience": "both",
        "is_gift_eligible": True,
        "specifications": {
            "Technologie": "SPE/PEM Électrolyse",
            "Capacité": "420ml bouteille premium",
            "Autonomie": "8 heures d'utilisation",
            "Charge": "USB-C rapide 2h",
            "Concentration H2": "1200-1600 PPB",
            "Matériaux": "Borosilicate + Titane"
        },
        "features": [
            "Enrichissement en hydrogène moléculaire H2",
            "Technologie SPE/PEM électrolyse avancée",
            "Bouteille 420ml en borosilicate premium",
            "Batterie lithium 8h d'autonomie",
            "Charge USB-C en 2h seulement",
            "Antioxydant naturel puissant",
            "Design ultra-portable et élégant",
            "LED indicateur de fonctionnement",
            "Compatible toutes eaux potables",
            "Parfait pour sport et voyage"
        ],
        "images_gallery": [
            "https://static.wixstatic.com/media/6af6bd_16baeaf62afc42009cf6ece2f46c767a~mv2.png/v1/fill/w_797,h_487,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Les%20b%C3%A9b%C3%A9s%20pleurent%20quand%20ils%20ont%20faim%2C%20ne%20peuvent%20pas%20attendre__%20c'est%20touj_20250220_19362.png"
        ],
        "in_stock": True
    },
    {
        "id": "fontaine-eau-animaux",
        "name": "Fontaine à Eau pour Animaux AquaPet Premium",
        "description": "Fontaine intelligente pour chiens et chats avec filtration avancée. Débit ajustable, niveau d'eau LED, matériaux premium sans BPA. Encourage l'hydratation naturelle de vos compagnons.",
        "price": 49.0,
        "original_price": 69.0,
        "image": "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png",
        "category": "animaux",
        "target_audience": "both",
        "is_gift_eligible": True,
        "specifications": {
            "Capacité": "2.4 litres",
            "Matériaux": "ABS premium sans BPA",
            "Filtration": "Triple filtration intégrée",
            "Pompe": "Ultra-silencieuse <40dB",
            "Alimentation": "5V USB",
            "Dimensions": "21×21×15 cm"
        },
        "features": [
            "Capacité généreuse 2.4 litres",
            "Triple système de filtration intégré",
            "Débit d'eau ajustable selon l'animal",
            "Niveau d'eau avec indicateur LED",
            "Pompe ultra-silencieuse <40dB",
            "Matériaux premium sans BPA",
            "Design ergonomique anti-dérapant",
            "Nettoyage facile - passage lave-vaisselle",
            "Encourage l'hydratation naturelle",
            "Compatible chiens et chats toutes tailles"
        ],
        "images_gallery": [
            "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png"
        ],
        "in_stock": True
    },
    
    # ======= OSMOSEUR B2B (maintenu) =======
    {
        "id": "osmoseur-pro",
        "name": "Système Osmose Inverse Professionnel BlueMountain Grand Format",
        "description": "Solution professionnelle BlueMountain grand format pour restaurants, bureaux et commerces. Dimensions 1040×330×300mm avec performance 15L/h.",
        "price": 1299.0,
        "original_price": 1599.0,
        "image": "https://www.josmoze.com/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
        "category": "osmoseur",
        "target_audience": "B2B",
        "product_tier": "professionnel",
        "specifications": {
            "Type": "BlueMountain Grand Format",
            "Dimensions": "1040×330×300mm",
            "Production": "15 litres/heure identique",
            "Installation": "Professionnelle incluse", 
            "Garantie": "5 ans pièces et main-d'œuvre",
            "Support": "Technique dédié professionnel"
        },
        "features": [
            "Système BlueMountain grand format pour entreprises",
            "Performance optimisée: 15L/h",
            "Production eau froide <10° - 4 litres/heure",
            "Production eau chaude >90° - 5 litres/heure",
            "Dimensions optimisées: 1040×330×300mm",
            "Installation professionnelle par technicien certifié",
            "Maintenance préventive incluse",
            "Formation du personnel à l'utilisation",
            "Support technique prioritaire B2B",
            "Certification sanitaire entreprise"
        ],
        "images_gallery": [
            "https://www.josmoze.com/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
            "https://www.josmoze.com/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
            "https://www.josmoze.com/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png"
        ],
        "in_stock": True
    },
    
    # ======= ACCESSOIRES (maintenus) =======
    {
        "id": "filtres-rechange",
        "name": "Kit Filtres de Rechange - 4 Étapes",
        "description": "Kit complet de filtres de rechange selon CDC. Kit 4 étapes : PP + GAC + CTO + Membrane UF. Qualité premium - À partir du 6ème mois - 59€.",
        "price": 59.0,
        "image": "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png",
        "category": "accessoire",
        "target_audience": "both",
        "specifications": {
            "Contenu": "4 cartouches complètes",
            "Compatibilité": "Tous systèmes Josmose", 
            "Fréquence": "Changement tous les 6 mois",
            "Qualité": "Filtres certifiés d'origine"
        },
        "features": [
            "Filtre PP - Polypropylène (grosses particules >5 microns)",
            "Filtre GAC - Charbon actif granulés (chlore + organiques)", 
            "Filtre CTO - Charbon actif bloc (reste chlore)",
            "Membrane Ultrafiltration (virus, bactéries, 0.01 micron)",
            "Compatible avec système principal",
            "Installation facile avec instructions",
            "Maintient efficacité optimale",
            "Cartouches à baïonnette"
        ],
        "in_stock": True
    },
    {
        "id": "filtres-pro",
        "name": "Filtres Professionnels - Pack Annuel",
        "description": "Pack de filtres professionnels pour systèmes industriels. Qualité supérieure avec suivi de maintenance.",
        "price": 89.0,
        "image": "https://www.josmoze.com/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png",
        "category": "accessoire",
        "target_audience": "B2B",
        "specifications": {
            "Compatibilité": "Systèmes professionnels BlueMountain",
            "Durée de vie": "12 mois",
            "Contenu": "8 cartouches premium + indicateurs"
        },
        "features": [
            "Filtres industriels haute performance",
            "Indicateurs de remplacement intelligent",
            "Maintenance programmée incluse",
            "Certification qualité professionnelle"
        ],
        "in_stock": True
    }
]

# Système de promotions
PROMOTION_RULES = {
    "launch_offer": {
        "eligible_products": ["osmoseur-premium", "osmoseur-prestige"],
        "gift_options": ["purificateur-portable-hydrogene", "fontaine-eau-animaux"],
        "description": "Offre de Lancement : 1 produit gratuit au choix avec achat Osmoseur Premium ou Prestige"
    }
}

# Système de parrainage
REFERRAL_SYSTEM = {
    "discount_percentage": 10,  # 10% de réduction pour le filleul
    "bonus_amount": 50,  # 50€ de bon d'achat pour le parrain
    "eligible_products": ["osmoseur-essentiel", "osmoseur-premium", "osmoseur-prestige"],
    "description": "Programme Parrainage : 10% pour le filleul, 50€ pour le parrain"
}