import os
import sys
import shutil
import uuid
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onizouka.settings")
import django
django.setup()

from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

SRC_DIR = r"C:\Users\a\Downloads\climatisur et ventilateur pack 1 ceux qui ont juste lzu prix d'achat"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Obtenir / Créer les Marques et Catégories
brand_fizzen, _ = Brand.objects.get_or_create(
    name="Fizzen",
    defaults={"slug": "fizzen", "is_active": True, "description": "Fizzen - Climatisation tropicalisée, ventilateurs solaires rechargeables et électroménager haute performance."}
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

cat_vent, _ = Category.objects.get_or_create(
    slug="climatisation",
    defaults={"name": "Climatisation & Ventilation", "is_active": True}
)

PRODUCTS_DATA = [
    {
        "name": 'Ventilateur Rechargeable Solaire Victor 18" FZ-Victor WRS-2888C',
        "category": cat_vent,
        "cost_price": 23000,
        "price": 30000,
        "sale_price": None,
        "stock": 15,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Ventilateur sur pied rechargeable 18 pouces avec roulettes de déplacement, autonomie jusqu'à 12h, batterie 12V 4.5Ah, compatible panneau solaire.",
        "description": "Le ventilateur rechargeable Victor 18 pouces (modèle FZ_Victor_WRS-2888C) est le compagnon idéal contre les fortes chaleurs et les coupures d'électricité à Bamako. Doté d'une puissante batterie 12V 4.5Ah et d'un moteur 100% cuivre pur, il offre 4 vitesses de souffle ultra-puissant et rafraîchissant. Équipé d'un panneau solaire compatible, de roulettes de déplacement 360°, d'une télécommande à distance, d'un port USB 5V pour recharger vos smartphones et de 18 lumières LED intégrées.",
        "specifications": {
            "Taille": '18 pouces (45 cm)',
            "Batterie": "12V 4.5Ah rechargeable",
            "Autonomie": "Jusqu'à 12 heures",
            "Moteur": "100% Cuivre pur",
            "Vitesses": "4 vitesses réglables",
            "Éclairage": "18 LED ultra-lumineuses intégrées",
            "Connectique": "Port USB 5V chargeur smartphone + Entrée solaire DC 12-15V",
            "Accessoires": "Télécommande sans fil + Roulettes 360°",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.55.jpeg"]
    },
    {
        "name": 'Ventilateur Rechargeable Solaire Tornado 18" FZ-Tornado RS-1830',
        "category": cat_vent,
        "cost_price": 21000,
        "price": 27500,
        "sale_price": None,
        "stock": 20,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Ventilateur vertical rechargeable 18\" grand souffle, moteur cuivre pur, batterie 12V 5Ah, télécommande et port USB.",
        "description": "Le ventilateur vertical Tornado 18 pouces (modèle FZ-Tornado RS-1830) garantit un débit d'air puissant et silencieux. Conçu pour le climat sahélien, il intègre un moteur en cuivre pur, une batterie haute durabilité 12V 5Ah, un contrôleur continu 9 vitesses et une télécommande. Dispose d'un port USB de charge mobile, d'une double sortie DC pour ampoules LED et d'une entrée directe pour panneau solaire.",
        "specifications": {
            "Taille": '18 pouces',
            "Batterie": "12V 5Ah plomb-acide",
            "Moteur": "Cuivre pur résistant",
            "Vitesses": "Contrôleur continu 9 vitesses",
            "Connectique": "Port USB 5V + Double sortie DC pour ampoules",
            "Compatibilité": "Fonctionne sur secteur 220V et Panneau Solaire",
            "Télécommande": "Oui incluse",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": [
            "WhatsApp Image 2026-11-26 at 19.56.46.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.38.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.23.jpeg"
        ]
    },
    {
        "name": 'Ventilateur Rechargeable Solaire Thunder 18" FZ-Thunder RS-118R',
        "category": cat_vent,
        "cost_price": 21000,
        "price": 27500,
        "sale_price": None,
        "stock": 18,
        "is_eco_solar": True,
        "is_featured": False,
        "short_description": "Ventilateur rechargeable 18\" à 5 pales de corne aérodynamiques, batterie 12V 5Ah, autonomie 2.5h à 12h, télécommande.",
        "description": "Le ventilateur sur pied rechargeable Thunder 18\" (modèle FZ_Thunder_RS-118R) se distingue par ses 5 pales de corne exclusives délivrant un flux d'air circulaire puissant. Équipé d'une batterie 12V 5Ah, d'une minuterie de 30 minutes, de 12 lampes LED brillantes et d'un port USB. Entièrement compatible panneau solaire.",
        "specifications": {
            "Taille": '18 pouces',
            "Pales": "5 pales profilées type corne",
            "Batterie": "12V 5Ah haute autonomie",
            "Autonomie": "2.5 à 12 heures",
            "Lumière": "12 pièces LED brillante",
            "Télécommande": "Oui",
            "Fonctions": "Port USB + Minuterie 0.5h + Compatible panneau solaire",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.49.jpeg"]
    },
    {
        "name": 'Ventilateur Rechargeable Solaire Diamond 16" FZ-Diamond RS-1630',
        "category": cat_vent,
        "cost_price": 19000,
        "price": 25000,
        "sale_price": None,
        "stock": 15,
        "is_eco_solar": True,
        "is_featured": False,
        "short_description": "Ventilateur vertical rechargeable 16 pouces corps incassable, batterie 12V 5Ah, moteur cuivre pur 9 vitesses.",
        "description": "Le ventilateur vertical Diamond 16\" (modèle FZ_Diamond_RS-1630) allie robustesse et élégance avec son corps incassable en polymère renforcé. Moteur 100% cuivre, batterie 12V 5Ah, contrôleur continu 9 vitesses, éclairage LED intégré et port USB 5V pour vos smartphones. Fonctionne sur secteur ou panneau solaire.",
        "specifications": {
            "Taille": '16 pouces',
            "Batterie": "12V 5Ah",
            "Moteur": "100% Cuivre pur",
            "Vitesses": "Contrôleur continu 9 vitesses",
            "Corps": "Structure renforcée incassable",
            "Connectique": "Port USB 5V + Double sortie DC ampoules LED",
            "Alimentation": "AC 110-240V / Entrée panneau solaire DC",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.43.jpeg"]
    },
    {
        "name": 'Pack Duo 2x Ventilateurs Rechargeables Aura 16" Silencieux',
        "category": cat_vent,
        "cost_price": 34000,
        "price": 45000,
        "sale_price": None,
        "stock": 12,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Pack économique de 2 ventilateurs rechargeables sans fil 16 pouces, autonomie longue durée 10 à 12 heures.",
        "description": "Offre exclusive Duo : 2 ventilateurs rechargeables Fizzen Aura 16 pouces. Profitez d'un rafraîchissement continu et silencieux de 10 à 12 heures selon la vitesse choisie. Idéal pour équiper deux pièces simultanément (chambre à coucher et salon ou bureau). Moteur silencieux à plusieurs niveaux de puissance.",
        "specifications": {
            "Conditionnement": "Pack de 2 ventilateurs complets (2 PCS)",
            "Taille": "16 pouces",
            "Autonomie": "10 à 12 heures sans fil",
            "Niveau sonore": "Ultra silencieux pour sommeil et travail",
            "Vitesse": "Plusieurs niveaux de puissance réglables",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.25.jpeg"]
    },
    {
        "name": 'Pack Duo 2x Ventilateurs Solaires Rechargeables Aura Deco 16" (RB-B16B)',
        "category": cat_vent,
        "cost_price": 34000,
        "price": 45000,
        "sale_price": None,
        "stock": 10,
        "is_eco_solar": True,
        "is_featured": False,
        "short_description": "Pack de 2 ventilateurs rechargeables 16\" design décoratif, batterie 6V 4.5Ah, 3 vitesses, veilleuse LED.",
        "description": "Pack Duo de 2 ventilateurs solaires rechargeables Aura Deco 16\" (modèle FZ_Aura Deco_RB-B16B). Finitions design bicolores rouge et bleu, batterie 6V 4.5Ah, autonomie 4.5h à 9h, oscillation grand angle gauche/droite pour une diffusion homogène de l'air frais. Équipé de lumières LED intégrées.",
        "specifications": {
            "Quantité": "2 Pièces complètes (Duo)",
            "Taille": "16 pouces",
            "Batterie": "6V 4.5Ah",
            "Autonomie": "4.5 à 9 heures",
            "Vitesses": "3 vitesses",
            "Éclairage": "Lumières LED intégrées",
            "Diffusion": "Oscillation panoramique gauche/droite",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.40.jpeg"]
    },
    {
        "name": "Humidificateur & Refroidisseur d'Air Évaporatif Rechargeable DC 20L avec Panneau Solaire",
        "category": cat_vent,
        "cost_price": 105000,
        "price": 135000,
        "sale_price": None,
        "stock": 8,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Refroidisseur d'air 20 Litres avec panneau solaire inclus, fonctionnement DC autonome, roulettes pivotantes.",
        "description": "Véritable climatiseur écologique par évaporation d'eau, l'humidificateur rechargeable Fizzen 20 Litres procure une sensation de fraîcheur intense même par 45°C à Bamako. Fonctionne avec le panneau solaire inclus pour une utilisation 100% gratuite le jour, ou sur sa batterie rechargeable. Réservoir 20L avec indicateur de niveau d'eau, volets oscillants automatiques, roulettes 360° robustes.",
        "specifications": {
            "Capacité réservoir": "20 Litres",
            "Énergie": "DC Solaire + Batterie rechargeable + Secteur",
            "Panneau solaire": "Panneau photovoltaïque inclus",
            "Mobilité": "4 roulettes multidirectionnelles 360°",
            "Technologie": "Refroidissement naturel par rideau d'eau évaporatif",
            "Oscillation": "Volets automatiques motorisés",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.18.jpeg"]
    },
    {
        "name": "Humidificateur & Refroidisseur d'Air Évaporatif Rechargeable DC 40L Grand Format avec Panneau Solaire",
        "category": cat_vent,
        "cost_price": 165000,
        "price": 215000,
        "sale_price": None,
        "stock": 6,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Refroidisseur grande capacité 40L, panneau solaire inclus, grande portée de fraîcheur pour salons et terrasses.",
        "description": "Le grand refroidisseur d'air Fizzen 40 Litres est conçu pour rafraîchir de vastes espaces résidentiels, cours couvertes, restaurants ou ateliers. Équipé d'un très grand panneau solaire photovoltaïque, d'un réservoir géant de 40 litres pour une autonomie d'eau de plusieurs jours, d'un panneau de contrôle à touches tactiles et de roulettes renforcées.",
        "specifications": {
            "Capacité réservoir": "40 Litres XXL",
            "Alimentation": "Double alimentation Solaire DC + Batterie + 220V",
            "Panneau solaire": "Grand panneau solaire haute puissance fourni",
            "Filtres": "Filtres alvéolaires latéraux et arrière haute fraîcheur",
            "Mobilité": "Roulettes industrielles avec freins",
            "Usage": "Idéal grandes pièces, salons, bureaux, plein air",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.21.jpeg"]
    },
    {
        "name": "Climatiseur Armoire sur Pied Fizzen 2.5 CV (24000 BTU) Tropicalisé",
        "category": cat_clim,
        "cost_price": 375000,
        "price": 475000,
        "sale_price": None,
        "stock": 5,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Climatiseur colonne vertical 2.5 chevaux haut de gamme, flux d'air puissant longue portée, écran digital.",
        "description": "Le climatiseur colonne armoire Fizzen 2.5 CV (24000 BTU) est la solution de climatisation prestige pour les espaces spacieux à Bamako. Design élégant et épuré blanc laqué, affichage digital LED central, soufflage vertical 3D grande vitesse, compresseur tropicalisé ultra-robuste adapté aux chaleurs extrêmes du Mali.",
        "specifications": {
            "Puissance": "2.5 CV (24000 BTU)",
            "Type": "Climatiseur Colonne Armoire Verticale",
            "Affichage": "Écran tactile digital LED",
            "Gaz": "Écologique haute performance",
            "Climat": "Tropicalisé T3 haute résistance",
            "Surface couverte": "Jusqu'à 40 m²",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.36.jpeg"]
    },
    {
        "name": "Climatiseur Armoire sur Pied Fizzen 3.0 CV (28000 BTU) Tropicalisé",
        "category": cat_clim,
        "cost_price": 425000,
        "price": 540000,
        "sale_price": None,
        "stock": 4,
        "is_eco_solar": False,
        "is_featured": False,
        "short_description": "Climatiseur armoire colonne 3.0 CV haute puissance, ventilation panoramique, climatisation instantanée.",
        "description": "Climatiseur armoire sur pied Fizzen 3.0 CV conçu pour les grandes salles de réunion, salons VIP, boutiques de luxe et restaurants. Son compresseur puissant assure une descente rapide en température. Panneau de commande moderne, télécommande longue portée, ailettes oscillantes motorisées.",
        "specifications": {
            "Puissance": "3.0 CV (28000 BTU)",
            "Format": "Armoire / Colonne sur pied",
            "Compresseur": "Tropicalisé T3 lourd",
            "Surface couverte": "Jusqu'à 55 m²",
            "Débit d'air": "Très grand débit turbo",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.36.jpeg"]
    },
    {
        "name": "Climatiseur Armoire sur Pied Fizzen 4.0 CV (36000 BTU) Tropicalisé",
        "category": cat_clim,
        "cost_price": 475000,
        "price": 595000,
        "sale_price": None,
        "stock": 3,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Climatiseur colonne industriel 4.0 CV puissance extrême pour très grands volumes et halls d'accueil.",
        "description": "Le fleuron de la gamme armoire Fizzen : 4.0 Chevaux (36000 BTU) pour une fraîcheur polaire même aux heures les plus chaudes. Conçu pour les salles de conférence, mosquées, églises, showrooms et résidences de standing. Filtres lavables anti-poussière et compresseur tropicalisé haute endurance.",
        "specifications": {
            "Puissance": "4.0 CV (36000 BTU)",
            "Type": "Armoire verticale grande puissance",
            "Compresseur": "Tropicalisé renforcé",
            "Surface couverte": "Jusqu'à 75 m²",
            "Fonctionnalités": "Mode Turbo, Déshumidification, Minuterie 24h",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.36.jpeg"]
    },
    {
        "name": "Climatiseur Split Mural Dual Inverter Fizzen 9000 BTU (1 CV) R410A 100% Cuivre",
        "category": cat_clim,
        "cost_price": 155000,
        "price": 195000,
        "sale_price": None,
        "stock": 15,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Climatiseur split 1 CV Dual Inverter, jusqu'à 70% d'économie d'énergie, 100% tuyaux en cuivre pur, gaz R410A.",
        "description": "Le Split Mural Dual Inverter Fizzen 9000 BTU (1 CV) allie silence absolu et économies d'électricité remarquables sur vos factures EDM. Grâce à sa technologie Dual Inverter avancée, il ajuste sa puissance en continu. Tuyauterie et radiateur 100% cuivre pur garanti (100% Pure Copper) anti-corrosion, tropicalisé T1/T3. Livré complet avec unité intérieure, unité extérieure et télécommande.",
        "specifications": {
            "Puissance": "9000 BTU (1.0 Cheval)",
            "Technologie": "Dual Inverter (jusqu'à -70% d'énergie)",
            "Matériau échangeur": "100% Cuivre pur garanti",
            "Gaz réfrigérant": "R410A écologique",
            "Surface recommandée": "12 à 18 m² (chambre, bureau)",
            "Mode": "Turbo Cooling, Sleep Mode, Auto Restart",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": [
            "WhatsApp Image 2026-11-26 at 19.56.26.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.30.jpeg"
        ]
    },
    {
        "name": "Climatiseur Split Mural Dual Inverter Fizzen 12000 BTU (1.5 CV) FZ-ACM-INV12K R410A",
        "category": cat_clim,
        "cost_price": 165000,
        "price": 215000,
        "sale_price": None,
        "stock": 20,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Split mural Dual Inverter 1.5 CV (12000 BTU) 100% cuivre, basse consommation, tropicalisé T1.",
        "description": "Le best-seller de la climatisation à Bamako : Split mural Fizzen Dual Inverter 12000 BTU (modèle officiel FZ-ACM-INV12K). Équipé d'un compresseur Dual Inverter éco-énergétique et de serpentins 100% cuivre pur. Refroidissement rapide en quelques minutes, affichage digital discret, gaz écologique R410A et fonctionnement ultra-silencieux.",
        "specifications": {
            "Modèle": "FZ-ACM-INV12K",
            "Puissance": "12000 BTU (1.5 Cheval)",
            "Technologie": "Dual Inverter haute efficacité",
            "Composants": "100% Pure Copper (Tuyauterie cuivre pur)",
            "Gaz": "R410A",
            "Surface recommandée": "18 à 28 m² (salon moyen, chambre principale)",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": [
            "WhatsApp Image 2026-11-26 at 19.56.28.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.26.jpeg"
        ]
    },
    {
        "name": "Climatiseur Split Mural Dual Inverter Fizzen 18000 BTU (2 CV) R410A 100% Cuivre",
        "category": cat_clim,
        "cost_price": 250000,
        "price": 320000,
        "sale_price": None,
        "stock": 10,
        "is_eco_solar": False,
        "is_featured": False,
        "short_description": "Split mural 2 CV (18000 BTU) Dual Inverter, grande capacité thermique pour salons et bureaux, 100% cuivre.",
        "description": "Climatiseur split mural Fizzen 18000 BTU (2 CV) Dual Inverter. Idéal pour les grands salons, bureaux professionnels et espaces ouverts jusqu'à 38 m². Alliant robustesse 100% cuivre et régulation inverter intelligente, il garantit un confort thermique parfait tout en maîtrisant la dépense électrique.",
        "specifications": {
            "Puissance": "18000 BTU (2.0 Chevaux)",
            "Technologie": "Dual Inverter économique",
            "Échangeur thermique": "100% Cuivre",
            "Gaz": "R410A",
            "Surface recommandée": "28 à 38 m²",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": [
            "WhatsApp Image 2026-11-26 at 19.56.30.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.26.jpeg"
        ]
    },
    {
        "name": "Climatiseur Split Mural Dual Inverter Fizzen 24000 BTU (2.5 CV) R410A 100% Cuivre",
        "category": cat_clim,
        "cost_price": 295000,
        "price": 380000,
        "sale_price": None,
        "stock": 8,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Split mural grande puissance 2.5 CV (24000 BTU) Dual Inverter 100% cuivre, tropicalisé grand salon.",
        "description": "Le Split mural Fizzen 24000 BTU (2.5 CV) Dual Inverter offre un débit d'air exceptionnel capable de refroidir efficacement jusqu'à 50 m². Système Dual Inverter réduisant les pics de consommation, compresseur tropicalisé et tuyauterie cuivre résistant aux conditions les plus rudes.",
        "specifications": {
            "Puissance": "24000 BTU (2.5 Chevaux)",
            "Technologie": "Dual Inverter",
            "Cuivre": "100% Cuivre pur haute résistance",
            "Surface recommandée": "38 à 50 m²",
            "Gaz": "R410A",
            "Garantie": "1 an Onizuka Shop"
        },
        "images": [
            "WhatsApp Image 2026-11-26 at 19.56.26.jpeg",
            "WhatsApp Image 2026-11-26 at 19.56.30.jpeg"
        ]
    },
    {
        "name": "Climatiseur Solaire Hybride AC/DC Inverter Fizzen 12000 BTU (1.5 CV) Connecté WiFi",
        "category": cat_clim,
        "cost_price": 550000,
        "price": 690000,
        "sale_price": None,
        "stock": 5,
        "is_eco_solar": True,
        "is_featured": True,
        "short_description": "Climatiseur solaire hybride AC/DC 1.5 CV : 0 FCFA d'électricité le jour ! Contrôle smartphone avec wattmètre intégré.",
        "description": "Révolution énergétique à Bamako : le Climatiseur Solaire Inverter Hybride Fizzen 12000 BTU (1.5 CV) fonctionne directement sur panneaux solaires photovoltaïques en journée sans passer par un onduleur ni batterie, réduisant votre facture EDM à zéro pendant les heures de fort ensoleillement ! En soirée ou par temps nuageux, il bascule automatiquement sur le réseau AC conventionnel. Doté d'une connexion WiFi pour contrôle complet via Smartphone (application avec affichage en temps réel de la puissance solaire consommée). Livré complet avec compresseur DC Inverter tropicalisé.",
        "specifications": {
            "Type": "Climatiseur Hybride Solaire AC-DC Inverter",
            "Puissance": "12000 BTU (1.5 Cheval)",
            "Alimentation": "Entrée directe photovoltaïque DC (jusqu'à 380V) + Entrée réseau AC 220V",
            "Économie": "Jusqu'à 100% d'économie en journée (0 FCFA le jour)",
            "Connectivité": "WiFi intégré + Application mobile avec suivi de puissance solaire (App Power Meter)",
            "Compresseur": "DC Inverter Tropicalisé T3",
            "Garantie": "2 ans Onizuka Shop"
        },
        "images": ["WhatsApp Image 2026-11-26 at 19.56.57.jpeg"]
    }
]

print(f"Insertion de {len(PRODUCTS_DATA)} produits réels Pack 1 Climatiseurs & Ventilateurs Fizzen...")

inserted_count = 0
for idx, pdata in enumerate(PRODUCTS_DATA, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-FZ-{idx:04d}"
    
    # Check if product already exists
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": pdata["category"],
            "brand": brand_fizzen,
            "cost_price": Decimal(str(pdata["cost_price"])),
            "price": Decimal(str(pdata["price"])),
            "sale_price": Decimal(str(pdata["sale_price"])) if pdata["sale_price"] else None,
            "stock": pdata["stock"],
            "min_stock": 3,
            "track_stock": True,
            "is_eco_solar": pdata["is_eco_solar"],
            "is_featured": pdata["is_featured"],
            "is_new": True,
            "is_active": True,
            "status": Product.Status.ACTIVE,
            "short_description": pdata["short_description"],
            "description": pdata["description"],
            "specifications": pdata["specifications"],
            "meta_title": f"{pdata['name']} - Prix Bamako Mali | Onizuka Shop",
            "meta_description": pdata["short_description"][:160]
        }
    )
    
    if not created:
        # Update existing
        product.cost_price = Decimal(str(pdata["cost_price"]))
        product.price = Decimal(str(pdata["price"]))
        product.stock = pdata["stock"]
        product.is_eco_solar = pdata["is_eco_solar"]
        product.save()

    # Images copying & ProductImage creation
    for img_order, img_filename in enumerate(pdata["images"]):
        src_path = os.path.join(SRC_DIR, img_filename)
        if os.path.exists(src_path):
            # Target filename
            clean_name = f"{slug[:40]}_{img_order+1}.jpeg"
            dst_path = os.path.join(MEDIA_PRODUCTS_DIR, clean_name)
            shutil.copy2(src_path, dst_path)
            
            # Relative path for ImageField
            rel_path = f"products/{clean_name}"
            
            # Create or update ProductImage
            pimg, img_created = ProductImage.objects.get_or_create(
                product=product,
                image=rel_path,
                defaults={
                    "is_primary": (img_order == 0),
                    "order": img_order,
                    "alt_text": f"{product.name} Onizuka Shop Bamako"
                }
            )
            if not pimg.is_primary and img_order == 0:
                pimg.is_primary = True
                pimg.save()
        else:
            print(f" [ATTENTION] Fichier introuvable: {src_path}")
            
    margin = product.margin
    margin_pct = product.margin_percentage
    print(f"[{idx}/{len(PRODUCTS_DATA)}] OK: {product.name} | Achat: {product.cost_price:,} F | Vente: {product.price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")
    inserted_count += 1

print(f"\nSuccès total ! {inserted_count} produits Fizzen réels insérés dans la base de données Onizuka Shop.")
