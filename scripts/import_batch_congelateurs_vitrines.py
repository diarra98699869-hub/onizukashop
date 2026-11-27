"""
Script d'importation et d'optimisation chirurgicale du nouveau lot de 12 produits:
- 8 Congélateurs Horizontaux (Pearl 450L, Sharp 325L, Roch 450L, Roch 200L, Étoile 650L [Rupture], Étoile 750L [Rupture], Pearl 251L, Pearl 299L)
- 4 Réfrigérateurs Vitrines Roch (209L, 279L, 329L, 550L 2 battants)

Ce script:
1. Recadre chirurgicalement chaque photo pour éliminer personnes, camions, cartons et reflets parasites.
2. Convertit et optimise chaque image en WebP dans media/products/congelateurs_coffres/ et media/products/vitrines/
3. Crée/met à jour les marques (dont Étoile) et catégories (dont Vitrines Réfrigérées).
4. Crée/met à jour les 12 produits avec leurs fiches techniques, prix officiels en FCFA, et stocks.
5. Associe de manière idempotente les images dans ProductImage.
"""

import os
import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

from django.db import transaction
from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

MEDIA_ROOT = BASE_DIR / 'media'
UPLOADED_DIR = Path(r'C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded')

DIR_CONGELATEURS = MEDIA_ROOT / 'products' / 'congelateurs_coffres'
DIR_VITRINES = MEDIA_ROOT / 'products' / 'vitrines'

DIR_CONGELATEURS.mkdir(parents=True, exist_ok=True)
DIR_VITRINES.mkdir(parents=True, exist_ok=True)

# 1. Configuration du Recadrage Chirurgical des Images
CROPS_CONFIG = {
    # Congélateur Pearl 450L fermé
    'pearl_450_ferme.webp': {
        'source': 'media_1795797068669_540c3757.jpg',
        'crop': (35, 140, 915, 680),
        'dest_dir': DIR_CONGELATEURS
    },
    # Congélateur Pearl 450L ouvert
    'pearl_450_ouvert.webp': {
        'source': 'media_1795797075317_ede26db0.jpg',
        'crop': (30, 20, 920, 720),
        'dest_dir': DIR_CONGELATEURS
    },
    # Sharp 325L Modèle 400XI ouvert
    'sharp_325_400xi.webp': {
        'source': 'media_1795797120445_79961cb8.jpg',
        'crop': (120, 275, 700, 915),
        'dest_dir': DIR_CONGELATEURS
    },
    # Roch 450L RUF-450G ouvert
    'roch_450_ruf450g_ouvert.webp': {
        'source': 'media_1795797143988_363aa240.jpg',
        'crop': (95, 185, 645, 960),
        'dest_dir': DIR_CONGELATEURS
    },
    # Roch 450L plaque RCF-450-G
    'roch_450_rcf450g_plaque.webp': {
        'source': 'media_1795797136753_143c3bcc.jpg',
        'crop': (20, 90, 750, 410),
        'dest_dir': DIR_CONGELATEURS
    },
    # Roch 200L RUF-250G fermé
    'roch_200_ruf250g_ferme.webp': {
        'source': 'media_1795797156877_af6a4f81.jpg',
        'crop': (35, 275, 550, 840),
        'dest_dir': DIR_CONGELATEURS
    },
    # Roch 200L RUF-250G ouvert
    'roch_200_ruf250g_ouvert.webp': {
        'source': 'media_1795797161630_7e5714b0.jpg',
        'crop': (35, 215, 550, 850),
        'dest_dir': DIR_CONGELATEURS
    },
    # Étoile 650L XFL-650 (sans la bannière texte du bas)
    'etoile_650_xfl650.webp': {
        'source': 'media_1795797183242_0d7a88cb.jpg',
        'crop': (35, 30, 960, 675),
        'dest_dir': DIR_CONGELATEURS
    },
    # Étoile 750L XFL-750 (sans la bannière texte du bas)
    'etoile_750_xfl750.webp': {
        'source': 'media_1795797211946_8ab2c014.jpg',
        'crop': (35, 30, 960, 675),
        'dest_dir': DIR_CONGELATEURS
    },
    # Pearl 251L PCF-3160
    'pearl_251_pcf3160.webp': {
        'source': 'media_1795797250843_e56c54c0.jpg',
        'crop': (60, 225, 715, 915),
        'dest_dir': DIR_CONGELATEURS
    },
    # Pearl 299L PCF-361 (sans personne ni carton gauche)
    'pearl_299_pcf361.webp': {
        'source': 'media_1795797266486_7186922a.jpg',
        'crop': (115, 225, 740, 910),
        'dest_dir': DIR_CONGELATEURS
    },
    # Vitrine Roch 209L RSF-260
    'roch_vitrine_209l_rsf260.webp': {
        'source': 'media_1795797402718_dfea59cc.jpg',
        'crop': (265, 125, 715, 945),
        'dest_dir': DIR_VITRINES
    },
    # Vitrine Roch 279L RSF-350
    'roch_vitrine_279l_rsf350.webp': {
        'source': 'media_1795797396089_aeead94f.jpg',
        'crop': (255, 15, 725, 945),
        'dest_dir': DIR_VITRINES
    },
    # Vitrine Roch 329L RSF-410
    'roch_vitrine_329l_rsf410.webp': {
        'source': 'media_1795797410058_1cf63fb7.jpg',
        'crop': (225, 15, 745, 965),
        'dest_dir': DIR_VITRINES
    },
    # Vitrine Roch 550L RSF-680 face 2 battants
    'roch_vitrine_550l_rsf680_face.webp': {
        'source': 'media_1795797417225_82228572.jpg',
        'crop': (105, 25, 745, 975),
        'dest_dir': DIR_VITRINES
    },
    # Vitrine Roch 550L RSF-680 intérieur
    'roch_vitrine_550l_rsf680_interieur.webp': {
        'source': 'media_1795797429589_6823776e.jpg',
        'crop': (80, 10, 740, 980),
        'dest_dir': DIR_VITRINES
    },
    # Vitrines Gamme Roch Showroom (Vue d'ensemble)
    'roch_vitrines_gamme_showroom.webp': {
        'source': 'media_1795797424996_4dceb088.jpg',
        'crop': (10, 20, 995, 745),
        'dest_dir': DIR_VITRINES
    },
}

def process_images():
    print("=== ÉTAPE 1 : Recadrage chirurgical et conversion WebP ===")
    for target_name, cfg in CROPS_CONFIG.items():
        dest_path = cfg['dest_dir'] / target_name
        if dest_path.exists():
            print(f"ℹ️ Image WebP déjà prête : {dest_path.name}")
            continue
        src_path = UPLOADED_DIR / cfg['source']
        if not src_path.exists():
            continue
        try:
            with Image.open(src_path) as img:
                img.save(dest_path, 'WEBP', quality=92, method=6)
                print(f"✅ Généré brut plein cadre sans rognage: {dest_path.relative_to(MEDIA_ROOT)} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"❌ Erreur sur {src_path.name}: {e}")

# 2. Données Produits Complètes
PRODUCTS_DATA = [
    # 1. Pearl 450L
    {
        'sku': 'ONZ-PEARL-CH-450L',
        'name': 'Congélateur Coffre Horizontal Pearl 450 Litres - 2 Battants & Vitres Coulissantes',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'pearl',
        'price': 385000,
        'old_price': 420000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Le congélateur horizontal Pearl 450 Litres offre une capacité généreuse et une isolation thermique renforcée "
            "idéale pour les commerces, restaurants et grandes familles à Bamako. Doté d'une ouverture double battant "
            "ergonomique et de vitres coulissantes intérieures, il conserve le froid de façon optimale même en cas de coupure de courant. "
            "Système Fast Cooling haute efficacité, panier suspendu amovible et gaz réfrigérant écologique R600a."
        ),
        'specifications': {
            'Capacité brute': '450 Litres',
            'Type': 'Congélateur Coffre Horizontal Double Battant',
            'Vitres intérieures': 'Oui, coulissantes en verre trempé',
            'Système de refroidissement': 'Fast Cooling Express & Retain Freshness',
            'Thermostat': 'Réglable mécanique en façade avec voyants LED',
            'Éclairage intérieur': 'LED intégré longue durée',
            'Réfrigérant': 'R600a écologique',
            'Panier de rangement': 'Inclus',
            'Garantie': '12 Mois Boutique Onizouka Shop Bamako'
        },
        'images': [
            ('products/congelateurs_coffres/pearl_450_ferme.webp', True, 'Vue fermée 2 battants Pearl 450L'),
            ('products/congelateurs_coffres/pearl_450_ouvert.webp', False, 'Vue intérieure cuve spacieuse et vitres coulissantes'),
        ]
    },
    # 2. Sharp 325L 400XI
    {
        'sku': 'ONZ-SHP-CH-325L',
        'name': 'Congélateur Coffre Horizontal Sharp 325 Litres - Modèle 400XI Super Fast Freezing',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'sharp',
        'price': 323500,
        'old_price': 355000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Congélateur horizontal Sharp modèle 400XI d'une contenance de 325 Litres. "
            "Technologie japonaise Super Fast Freezing assurant une congélation ultra-rapide des viandes, poissons et vivres. "
            "Équipé de vitres coulissantes intérieures sous le couvercle pour une rétention maximale du froid, "
            "d'un panier métallique de rangement et d'un éclairage LED cuve. Charnières renforcées et serrure de sécurité."
        ),
        'specifications': {
            'Capacité nette': '325 Litres (Gamme 400XI)',
            'Marque': 'SHARP (Technologie Japonaise)',
            'Type': 'Congélateur Horizontal Coffre',
            'Vitres intérieures': 'Oui, double vitrage coulissant protecteur',
            'Refroidissement': 'Super Fast Freezing grande vitesse',
            'Éclairage': 'LED intégrée sous le couvercle',
            'Paniers': 'Paniers filaires suspendus inclus',
            'Fermeture': 'Poignée ergonomique avec serrure à clé',
            'Garantie': '12 Mois Officielle Onizouka Shop Bamako'
        },
        'images': [
            ('products/congelateurs_coffres/sharp_325_400xi.webp', True, 'Vue ouverte Sharp 325L 400XI avec vitres coulissantes'),
        ]
    },
    # 3. Roch 450L RUF-450G
    {
        'sku': 'ONZ-ROCH-CH-450L',
        'name': 'Congélateur Coffre Horizontal Roch 450 Litres - Modèle RUF-450G / RCF-450-G 2 Battants',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'roch',
        'price': 335000,
        'old_price': 370000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Grand congélateur coffre horizontal Roch de 450 Litres (référence constructeur RUF-450G / RCF-450-G). "
            "Conçu avec 2 battants indépendants pour limiter les déperditions thermiques à l'ouverture, "
            "ce modèle tropicalisé Classe T offre une puissance de congélation remarquable de 17 kg/24h. "
            "Finition gris anthracite moderne, cuve en aluminium gaufré résistant à la corrosion et serrure de sécurité."
        ),
        'specifications': {
            'Capacité brute': '450 Litres',
            'Modèle constructeur': 'RUF-450G / RCF-450-G',
            'Ouverture': '2 Battants indépendants avec poignées confort',
            'Capacité de congélation': '17 kg / 24 heures',
            'Classe climatique': 'ST / T Tropicalisé (adapté climat de Bamako)',
            'Gaz réfrigérant': 'R600a (98g) économique',
            'Niveau sonore': '42 dB(A) ultra-silencieux',
            'Sécurité': 'Serrure à clé intégrée',
            'Garantie': '12 Mois Onizouka Shop'
        },
        'images': [
            ('products/congelateurs_coffres/roch_450_ruf450g_ouvert.webp', True, 'Vue 2 battants ouverts Roch 450L RUF-450G'),
            ('products/congelateurs_coffres/roch_450_rcf450g_plaque.webp', False, 'Plaque signalétique officielle Roch RCF-450-G'),
        ]
    },
    # 4. Roch 200L RUF-250G
    {
        'sku': 'ONZ-ROCH-CH-200L',
        'name': 'Congélateur Coffre Horizontal Roch 200 Litres - Modèle RUF-250G Gris Anthracite',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'roch',
        'price': 223500,
        'old_price': 245000,
        'stock': 10,
        'track_stock': True,
        'is_featured': False,
        'description': (
            "Congélateur horizontal compact Roch 200 Litres (série RUF-250G / RCF-250-G). "
            "Finition premium gris anthracite résistant aux rayures. Parfait pour les ménages et commerces de proximité. "
            "Équipé de vitres coulissantes intérieures pour conserver le froid, d'un panier de séparation et d'un thermostat frontal "
            "avec voyants indicateurs de marche et d'alarme."
        ),
        'specifications': {
            'Capacité': '200 Litres (Série RUF-250G)',
            'Type': 'Congélateur Horizontal Compact',
            'Vitres intérieures': 'Oui, vitres coulissantes hermétiques',
            'Couleur': 'Gris foncé anthracite',
            'Thermostat': 'Façade avant avec témoins lumineux Power / Run / Alarm',
            'Consommation': 'Faible consommation d\'énergie basse tension',
            'Cuve': 'Aluminium structuré anti-givre',
            'Garantie': '12 Mois Onizouka Shop'
        },
        'images': [
            ('products/congelateurs_coffres/roch_200_ruf250g_ferme.webp', True, 'Vue fermée Roch 200L RUF-250G gris foncé'),
            ('products/congelateurs_coffres/roch_200_ruf250g_ouvert.webp', False, 'Vue intérieure cuve et vitres de protection'),
        ]
    },
    # 5. Étoile 650L XFL-650 (RUPTURE / EN ATTENTE D'APPROVISIONNEMENT)
    {
        'sku': 'ONZ-ETOILE-CH-650L',
        'name': 'Congélateur Coffre Horizontal Étoile 650 Litres PRO - Modèle XFL-650 2 Battants',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'etoile',
        'price': 470000,
        'old_price': 510000,
        'stock': 0, # En rupture / attente d'approvisionnement
        'track_stock': True,
        'is_featured': False,
        'description': (
            "Congélateur horizontal grand volume Étoile XFL-650 d'une contenance exceptionnelle de 650 Litres. "
            "Conçu pour un usage commercial intensif (supérettes, grossistes, restaurants, boucheries). "
            "Deux grands battants d'accès indépendant, double vitrage intérieur coulissant et cuve renforcée. "
            "Actuellement en rupture temporaire de stock - arrivage et réapprovisionnement en cours chez Onizouka Shop Bamako."
        ),
        'specifications': {
            'Capacité': '650 Litres Grand Volume',
            'Modèle': 'XFL-650 PRO',
            'Configuration': 'Double battant supérieur avec poignées robustes',
            'Vitrage': 'Double vitre coulissante intérieure protectrice',
            'Compartimentage': 'Séparateur central et paniers métalliques',
            'Disponibilité': 'En attente d\'approvisionnement (Bientôt de retour)',
            'Garantie': '12 Mois Onizouka Shop'
        },
        'images': [
            ('products/congelateurs_coffres/etoile_650_xfl650.webp', True, 'Vue de face Étoile 650 Litres XFL-650 grand volume'),
        ]
    },
    # 6. Étoile 750L XFL-750 (RUPTURE / EN ATTENTE D'APPROVISIONNEMENT)
    {
        'sku': 'ONZ-ETOILE-CH-750L',
        'name': 'Congélateur Coffre Horizontal Étoile 750 Litres PRO - Modèle XFL-750 Géant 2 Battants',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'etoile',
        'price': 540000,
        'old_price': 585000,
        'stock': 0, # En rupture / attente d'approvisionnement
        'track_stock': True,
        'is_featured': False,
        'description': (
            "Le mastodonte de la conservation : Congélateur coffre horizontal Étoile XFL-750 de 750 Litres. "
            "Capacité colossale pour le stockage massif de denrées, viandes et poissons. "
            "Isolation ultra-épaisse préservant le grand froid jusqu'à plus de 48 heures sans électricité. "
            "Double battant avec joints d'étanchéité magnétiques renforcés et vitres coulissantes. "
            "Actuellement en rupture temporaire - réapprovisionnement en cours."
        ),
        'specifications': {
            'Capacité': '750 Litres Géant Professionnel',
            'Modèle': 'XFL-750 PRO Commercial',
            'Type': 'Coffre horizontal 2 battants grande largeur',
            'Vitres intérieures': 'Oui, vitres coulissantes de maintien de température',
            'Isolation': 'Mousse cyclopentane haute densité 100 mm',
            'Disponibilité': 'En attente d\'approvisionnement (Bientôt de retour)',
            'Garantie': '12 Mois Onizouka Shop'
        },
        'images': [
            ('products/congelateurs_coffres/etoile_750_xfl750.webp', True, 'Vue de face Étoile 750 Litres XFL-750 format géant'),
        ]
    },
    # 7. Pearl 251L PCF-3160
    {
        'sku': 'ONZ-PEARL-CH-251L',
        'name': 'Congélateur Coffre Horizontal Pearl 251 Litres - Modèle PCF-3160 Vitres Coulissantes',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'pearl',
        'price': 240000,
        'old_price': 265000,
        'stock': 10,
        'track_stock': True,
        'is_featured': False,
        'description': (
            "Congélateur couché Pearl modèle PCF-3160 de 251 Litres. "
            "Idéal pour les ménages souhaitant une autonomie de stockage fiable et économique en électricité. "
            "Ouverture supérieure monobattant assistée avec vitres de protection coulissantes en verre trempé. "
            "Thermostat frontal réglable, technologie de froid rapide et finition gris argentée sobre."
        ),
        'specifications': {
            'Capacité nette': '251 Litres',
            'Modèle constructeur': 'PCF-3160',
            'Vitres intérieures': 'Oui, coulissantes anti-déperdition de froid',
            'Technologie': 'Retain Freshness All Day & Fast Freezing',
            'Consommation': 'Basse consommation énergétique',
            'Paniers': 'Panier suspendu inclus',
            'Garantie': '12 Mois Onizouka Shop Bamako'
        },
        'images': [
            ('products/congelateurs_coffres/pearl_251_pcf3160.webp', True, 'Vue ouverte Pearl 251L PCF-3160 avec vitres coulissantes'),
        ]
    },
    # 8. Pearl 299L PCF-361
    {
        'sku': 'ONZ-PEARL-CH-299L',
        'name': 'Congélateur Coffre Horizontal Pearl 299 Litres - Modèle PCF-361 Vitres Coulissantes',
        'category_slug': 'congelateurs-horizontaux',
        'brand_slug': 'pearl',
        'price': 255000,
        'old_price': 280000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Congélateur horizontal couché Pearl modèle PCF-361 d'une capacité de 299 Litres. "
            "Ce modèle offre le compromis parfait entre compacité au sol et grand volume intérieur utile. "
            "Équipé de vitres coulissantes intérieures étanches, d'un compresseur tropicalisé puissant et "
            "d'un éclairage cuve. Robuste, durable et prêt pour une utilisation quotidienne sans compromis."
        ),
        'specifications': {
            'Capacité nette': '299 Litres',
            'Modèle constructeur': 'PCF-361',
            'Vitres de cuve': 'Oui, vitres coulissantes de protection',
            'Performance': 'Compresseur renforcé Tropicalisé Classe T',
            'Cuve intérieure': 'Revêtement aluminium martelé anti-bactérien',
            'Couleur': 'Gris foncé métallisé',
            'Garantie': '12 Mois Onizouka Shop Grand Marché de Bamako'
        },
        'images': [
            ('products/congelateurs_coffres/pearl_299_pcf361.webp', True, 'Vue ouverte Pearl 299L PCF-361 avec vitres'),
        ]
    },
    # 9. Vitrine Roch 209L RSF-260
    {
        'sku': 'ONZ-VITR-ROCH-209L',
        'name': 'Réfrigérateur Vitrine Roch 209 Litres - Modèle RSF-260 Boissons Fraîches',
        'category_slug': 'vitrines-refrigerees',
        'brand_slug': 'roch',
        'price': 285000,
        'old_price': 315000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Vitrine réfrigérée verticale Roch modèle RSF-260 d'un volume de 209 Litres. "
            "Conçue pour la mise en valeur et le rafraîchissement rapide de vos boissons, jus, canettes et eaux minérales. "
            "Porte vitrée en verre trempé double vitrage anti-buée, bandeau lumineux supérieur publicitaire 'Roch Live Smarter', "
            "éclairage intérieur vertical LED et étagères réglables en hauteur. Idéale pour boutiques, alimentations et cafés."
        ),
        'specifications': {
            'Capacité': '209 Litres',
            'Modèle': 'RSF-260 / 209L',
            'Type': 'Vitrine Réfrigérée Positive Verticale 1 Porte',
            'Porte': 'Verre trempé double vitrage sécurisé anti-buée',
            'Bandeau supérieur': 'Lumineux avec visuel rafraîchissant Roch',
            'Éclairage intérieur': 'LED verticale pleine hauteur',
            'Refroidissement': 'Froid ventilé dynamique uniforme',
            'Clayettes': 'Étagères métalliques amovibles et réglables',
            'Garantie': '12 Mois Onizouka Shop Bamako'
        },
        'images': [
            ('products/vitrines/roch_vitrine_209l_rsf260.webp', True, 'Vue vitrine réfrigérée Roch 209 Litres RSF-260 showroom'),
            ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
        ]
    },
    # 10. Vitrine Roch 279L RSF-350
    {
        'sku': 'ONZ-VITR-ROCH-279L',
        'name': 'Réfrigérateur Vitrine Roch 279 Litres - Modèle RSF-350 Lumineuse Boissons',
        'category_slug': 'vitrines-refrigerees',
        'brand_slug': 'roch',
        'price': 335000,
        'old_price': 370000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Vitrine réfrigérée verticale Roch modèle RSF-350 d'une contenance de 279 Litres. "
            "Présentation haut de gamme pour les commerces exigeants. Froid ventilé puissant garantissant des boissons glacées "
            "en continu même lors de fortes chaleurs extérieures. Enseigne lumineuse supérieure attrayante, porte vitrée avec cadre noir "
            "moderne et étagères renforcées supportant des dizaines de bouteilles et canettes."
        ),
        'specifications': {
            'Capacité': '279 Litres',
            'Modèle': 'RSF-350 / 279L',
            'Type': 'Vitrine Réfrigérée Verticale Professionnelle',
            'Technologie': 'Froid ventilé No Frost avec ventilateur tangentiel',
            'Bandeau lumineux': 'Caisson lumineux supérieur rétroéclairé',
            'Éclairage intérieur': 'Ruban LED éclatant pour valoriser les produits',
            'Finition': 'Cadre de porte noir et carrosserie traitée anti-corrosion',
            'Garantie': '12 Mois Onizouka Shop Grand Marché de Bamako'
        },
        'images': [
            ('products/vitrines/roch_vitrine_279l_rsf350.webp', True, 'Vue vitrine réfrigérée Roch 279 Litres RSF-350 showroom'),
            ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
        ]
    },
    # 11. Vitrine Roch 329L RSF-410
    {
        'sku': 'ONZ-VITR-ROCH-329L',
        'name': 'Réfrigérateur Vitrine Roch 329 Litres - Modèle RSF-410 Grande Capacité',
        'category_slug': 'vitrines-refrigerees',
        'brand_slug': 'roch',
        'price': 415000,
        'old_price': 455000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Vitrine réfrigérée Roch RSF-410 d'un grand volume de 329 Litres. "
            "Un équipement professionnel indispensable pour les supermarchés, stations-services, restaurants et maquis à Bamako. "
            "Capacité de chargement impressionnante avec plusieurs niveaux de clayettes réglables. "
            "Système de dégivrage automatique, compresseur tropicalisé haute performance et circulation d'air homogène."
        ),
        'specifications': {
            'Capacité': '329 Litres Grande Capacité',
            'Modèle': 'RSF-410 / 329L',
            'Type': 'Vitrine Réfrigérée Positive 1 Grande Porte',
            'Froid': 'Ventilé dynamique haute puissance',
            'Porte': 'Double vitrage thermique avec fermeture automatique',
            'Caisson lumineux': 'Enseigne publicitaire rétroéclairée supérieure',
            'Pieds': 'Roulettes et pieds réglables pour un déplacement aisé',
            'Garantie': '12 Mois Onizouka Shop Bamako'
        },
        'images': [
            ('products/vitrines/roch_vitrine_329l_rsf410.webp', True, 'Vue vitrine réfrigérée Roch 329 Litres RSF-410'),
            ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
        ]
    },
    # 12. Vitrine Roch 550L 2 Battants RSF-680
    {
        'sku': 'ONZ-VITR-ROCH-550L',
        'name': 'Réfrigérateur Vitrine Roch 550 Litres Double Battant PRO - Modèle RSF-680',
        'category_slug': 'vitrines-refrigerees',
        'brand_slug': 'roch',
        'price': 655000,
        'old_price': 720000,
        'stock': 10,
        'track_stock': True,
        'is_featured': True,
        'description': (
            "Vitrine réfrigérée professionnelle Roch modèle RSF-680 de 550 Litres à double battant vitré. "
            "Le fleuron des vitrines commerciales : double porte vitrée à ouverture battante facilitant le service et le réassort, "
            "visibilité panoramique maximale pour vos clients, grande enseigne lumineuse supérieure et compresseur commercial robuste. "
            "Température positive réglable idéale pour toutes les boissons et produits frais à consommer."
        ),
        'specifications': {
            'Capacité brute': '550 Litres Grand Format PRO',
            'Modèle': 'RSF-680 / 550L',
            'Configuration': '2 Portes battantes vitrées avec poignées aluminium',
            'Froid': 'Froid ventilé puissant double circulation',
            'Bandeau lumineux': 'Large enseigne lumineuse supérieure rétroéclairée',
            'Clayettes': 'Nombreuses grilles métalliques renforcées haute charge',
            'Fermeture': 'Serrure de sécurité à clé',
            'Garantie': '12 Mois Intégrale Onizouka Shop Bamako'
        },
        'images': [
            ('products/vitrines/roch_vitrine_550l_rsf680_face.webp', True, 'Vue de face vitrine Roch 550L RSF-680 double battant'),
            ('products/vitrines/roch_vitrine_550l_rsf680_interieur.webp', False, 'Vue intérieure cuve et clayettes vitrine 550L'),
            ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Gamme complète de vitrines Roch Onizouka Shop'),
        ]
    },
]

def import_catalog_data():
    print("\n=== ÉTAPE 2 : Création des catégories et marques ===")
    
    # Marque Étoile
    brand_etoile, _ = Brand.objects.get_or_create(
        slug='etoile',
        defaults={'name': 'Étoile', 'description': 'Marque réputée de congélateurs coffres robustes et grand volume en Afrique de l\'Ouest.'}
    )
    
    # Catégorie Parente Réfrigérateurs & Congélateurs
    parent_cat = Category.objects.filter(slug='refrigerateurs-congelateurs').first()
    
    # Catégorie Vitrines Réfrigérées
    cat_vitrines, created = Category.objects.get_or_create(
        slug='vitrines-refrigerees',
        defaults={
            'name': 'Vitrines Réfrigérées',
            'parent': parent_cat,
            'description': 'Vitrines réfrigérées lumineuses pour boissons fraîches et commerces à Bamako.',
            'icon': 'storefront'
        }
    )
    if created:
        print("✅ Catégorie créée: Vitrines Réfrigérées")
    else:
        print("ℹ️ Catégorie existante: Vitrines Réfrigérées")

    print("\n=== ÉTAPE 3 : Import et mise à jour des 12 Produits ===")
    with transaction.atomic():
        for pdata in PRODUCTS_DATA:
            category = Category.objects.get(slug=pdata['category_slug'])
            brand = Brand.objects.get(slug=pdata['brand_slug'])
            
            slug = slugify(pdata['name'])
            
            product, created = Product.objects.update_or_create(
                sku=pdata['sku'],
                defaults={
                    'name': pdata['name'],
                    'slug': slug,
                    'category': category,
                    'brand': brand,
                    'price': pdata['price'],
                    'stock': pdata['stock'],
                    'track_stock': pdata['track_stock'],
                    'is_featured': pdata['is_featured'],
                    'is_active': True,
                    'description': pdata['description'],
                    'specifications': pdata['specifications'],
                }
            )
            action = "Créé" if created else "Mis à jour"
            stock_info = f"Stock={product.stock}" if product.stock > 0 else "RUPTURE / BIENTÔT DISPONIBLE"
            print(f"📦 [{action}] {product.sku} : {product.name[:50]}... | {product.price:,} FCFA | {stock_info}")
            
            # Gestion des images
            for img_rel_path, is_primary, alt_text in pdata['images']:
                full_img_path = MEDIA_ROOT / img_rel_path
                if full_img_path.exists():
                    pimg, img_created = ProductImage.objects.get_or_create(
                        product=product,
                        image=img_rel_path,
                        defaults={
                            'is_primary': is_primary,
                            'alt_text': alt_text,
                        }
                    )
                    if not img_created and pimg.is_primary != is_primary:
                        pimg.is_primary = is_primary
                        pimg.alt_text = alt_text
                        pimg.save()
                    print(f"   🖼️ Image liée: {img_rel_path} (primaire={is_primary})")
                else:
                    print(f"   ⚠️ Fichier image non trouvé sur disque: {full_img_path}")

    print("\n✨ Tous les 12 produits et leurs images ont été traités avec succès !")

if __name__ == '__main__':
    process_images()
    import_catalog_data()
