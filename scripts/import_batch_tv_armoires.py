"""
Script d'importation et d'optimisation chirurgicale des 29 nouveaux produits:
- 9 Téléviseurs East Point (32" à 75", 2 télécommandes, décodeur intégré, 4K/FHD, garantie 1 an)
- 8 Téléviseurs Fizzen (32" à 85", webOS & Android, Magic Remote, 4K/FHD, garantie 1 an)
- 7 Téléviseurs Samsung Authentique (32" à 85", Crystal UHD 4K & Full HD Smart)
- 5 Armoires de Chambre Haute Qualité (2 et 3 portes, livraison et installation offertes à Bamako)
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

DIR_TV = MEDIA_ROOT / 'products' / 'televiseurs'
DIR_MEUBLES = MEDIA_ROOT / 'products' / 'meubles'

DIR_TV.mkdir(parents=True, exist_ok=True)
DIR_MEUBLES.mkdir(parents=True, exist_ok=True)

# 1. Traitement et Optimisation des Images en WebP
IMAGE_PROCESS_PLAN = {
    # --- EAST POINT ---
    'ep_showroom_stack.webp': {
        'source': 'media_1795808729064_3e51cefb.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'ep_32_box.webp': {
        'source': 'media_1795808762915_fa903519.jpg',
        'crop': (20, 20, 1004, 750),
        'dest': DIR_TV
    },
    'ep_43_box.webp': {
        'source': 'media_1795808770359_727c19ed.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'ep_50_box.webp': {
        'source': 'media_1795808779505_19d4c366.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'ep_55_box.webp': {
        'source': 'media_1795808785760_393bf64f.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'ep_65_box.webp': {
        'source': 'media_1795808791971_8e7bc1d5.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'ep_75_box.webp': {
        'source': 'media_1795808755512_9a84eb19.jpg',
        'crop': None,
        'dest': DIR_TV
    },

    # --- FIZZEN ---
    'fizzen_43_lifestyle.webp': {
        'source': 'media_1795808854068_c5a294a6.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_webos_hub.webp': {
        'source': 'media_1795808861567_3bd38ed5.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_frameless_screen.webp': {
        'source': 'media_1795808869117_eff01588.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_diamond_webos_box.webp': {
        'source': 'media_1795808876837_f7145b40.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_gold_android_box.webp': {
        'source': 'media_1795808882590_724c5adb.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_diamond_75_box.webp': {
        'source': 'media_1795808898175_b07a844d.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'fizzen_box_large.webp': {
        'source': 'media_1795808908732_77d2f562.jpg',
        'crop': None,
        'dest': DIR_TV
    },

    # --- SAMSUNG ---
    'samsung_store_stack.webp': {
        'source': 'media_1795808993253_f9daa613.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_smart_hub.webp': {
        'source': 'media_1795809002266_d9d266b6.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_crystal_front.webp': {
        'source': 'media_1795809009312_2f264c4d.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_slim_wall.webp': {
        'source': 'media_1795809027218_d0097e2e.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_32_stand.webp': {
        'source': 'media_1795809037688_6dcc50c8.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_remote_view.webp': {
        'source': 'media_1795809047839_e7be5f4c.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_living_wall.webp': {
        'source': 'media_1795809056392_83eccd29.jpg',
        'crop': None,
        'dest': DIR_TV
    },
    'samsung_slim_angle.webp': {
        'source': 'media_1795809063589_7d78ecf0.jpg',
        'crop': (0, 75, 712, 533), # rogner gribouillage feutre rouge en haut
        'dest': DIR_TV
    },
    'samsung_crystal_uhd_face.webp': {
        'source': 'media_1795809070079_146157d1.jpg',
        'crop': None,
        'dest': DIR_TV
    },

    # --- ARMOIRES ---
    'armoire_2p_bois_marron.webp': {
        'source': 'media_1795809117460_fafce0bc.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_3p_bois_marron.webp': {
        'source': 'media_1795809287456_b18391bc.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_blanche_face.webp': {
        'source': 'media_1795809318775_289b05c3.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_blanche_interieur.webp': {
        'source': 'media_1795809327503_d54fe59d.png',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_rouge_acajou.webp': {
        'source': 'media_1795809370578_64c2e580.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_bicolore_fermee.webp': {
        'source': 'media_1795809383417_b3986636.png',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_bicolore_interieur.webp': {
        'source': 'media_1795809387669_1c545522.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_bicolore_face.webp': {
        'source': 'media_1795809397312_5c6cca5f.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
    'armoire_2p_bicolore_magasin.webp': {
        'source': 'media_1795809402839_e1f29668.jpg',
        'crop': None,
        'dest': DIR_MEUBLES
    },
}

def process_images():
    print("=== 1. CONVERSION ET OPTIMISATION WEBP DES IMAGES ===")
    for target_name, config in IMAGE_PROCESS_PLAN.items():
        src_file = UPLOADED_DIR / config['source']
        dest_file = config['dest'] / target_name
        
        if not src_file.exists():
            print(f"  [ATTENTION] Fichier source introuvable: {src_file.name}")
            continue

        im = Image.open(src_file)
        if im.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            if im.mode == 'P':
                im = im.convert('RGBA')
            bg.paste(im, mask=im.split()[-1] if im.mode == 'RGBA' else None)
            im = bg

        if config['crop']:
            im = im.crop(config['crop'])

        im.save(dest_file, format='WEBP', quality=88, method=6)
        print(f"  [OK] {target_name} ({im.size[0]}x{im.size[1]}px) -> {dest_file.relative_to(MEDIA_ROOT)}")


# 2. DEFINITION DES 29 PRODUITS
PRODUCTS_DATA = [
    # ==========================================
    # EAST POINT (9 modèles)
    # ==========================================
    {
        'sku': 'ONZ-TV-EP-32S',
        'name': 'Téléviseur East Point 32" Simple LED HD - Décodeur Intégré',
        'slug': 'televiseur-east-point-32-pouces-simple-led-hd',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 57500,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': False,
        'short_description': 'TV East Point 32 pouces HD avec décodeur intégré TNT/Satellite et double télécommande. Garantie 1 an constructeur.',
        'description': (
            "Nouvel arrivage officiel chez Onizouka Shop Bamako !\n\n"
            "Le téléviseur East Point 32 pouces Simple offre une qualité d'image HD lumineuse et nette, "
            "idéale pour le salon, la chambre ou les espaces professionnels.\n\n"
            "Points forts :\n"
            "- Double télécommande d'origine incluse\n"
            "- Décodeur numérique intégré (TNT / Satellite direct sans box externe)\n"
            "- Connectivité complète : HDMI, USB multimédia (vidéos, musiques, photos), AV\n"
            "- Basse consommation d'énergie adaptée au réseau électrique malien\n"
            "- Garantie officielle 1 an avec service après-vente à Bamako"
        ),
        'specifications': {
            'Taille écran': '32 pouces (80 cm)',
            'Résolution': 'HD 1366 x 768 pixels',
            'Décodeur': 'Intégré (DVB-T2/S2)',
            'Accessoires': '2 télécommandes fournies',
            'Connectique': '2x HDMI, 2x USB, AV, Sortie Audio',
            'Alimentation': '100-240V, 50/60Hz',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_32_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-32SM',
        'name': 'Smart TV East Point 32" Smart LED HD - WiFi & Décodeur Intégré',
        'slug': 'smart-tv-east-point-32-pouces-smart-led-hd-wifi',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 67500,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV East Point 32" connectée avec WiFi, YouTube, Prime Video, décodeur intégré et 2 télécommandes. Garantie 1 an.',
        'description': (
            "Découvrez la Smart TV East Point 32 pouces connectée chez Onizouka Shop Bamako.\n\n"
            "Profitez d'un accès direct à YouTube, Netflix et vos applications préférées grâce au WiFi intégré. "
            "Livrée avec 2 télécommandes et décodeur intégré direct.\n\n"
            "Caractéristiques :\n"
            "- Système Smart TV connecté rapide et fluide\n"
            "- WiFi intégré et port réseau RJ45\n"
            "- 2 télécommandes d'origine incluses\n"
            "- Décodeur satellite et terrestre intégré\n"
            "- Garantie 1 an assurée par Onizouka Shop"
        ),
        'specifications': {
            'Taille écran': '32 pouces (80 cm)',
            'Type': 'Smart TV connectée WiFi',
            'Applications': 'YouTube, Netflix, Prime Video, Navigateur',
            'Décodeur': 'Intégré TNT / Satellite',
            'Accessoires': '2 télécommandes incluses',
            'Connectique': 'WiFi, HDMI, USB, RJ45 Ethernet',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_32_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-43SM',
        'name': 'Smart TV East Point 43" 4K Ultra HD Smart - 2 Télécommandes',
        'slug': 'smart-tv-east-point-43-pouces-4k-ultra-hd-smart',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 127500,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV East Point 43 pouces 4K Ultra HD, 2 télécommandes, décodeur intégré, YouTube, Netflix. Garantie 1 an.',
        'description': (
            "Arrivage exceptionnel East Point 43 pouces 4K Smart chez Onizouka Shop !\n\n"
            "Vivez une expérience cinéma avec une résolution 4K Ultra HD éblouissante. "
            "Équipée de 2 télécommandes, d'un décodeur intégré et de toutes les applications de streaming.\n\n"
            "- Image 4K Ultra HD haute fidélité\n"
            "- Smart TV connectée WiFi + Ethernet\n"
            "- 2 télécommandes incluses pour un confort d'usage optimal\n"
            "- Décodeur TNT et Satellite intégré\n"
            "- Garantie 1 an Onizouka Shop"
        ),
        'specifications': {
            'Taille écran': '43 pouces (108 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'Smart TV connectée',
            'Décodeur': 'Intégré DVB-T2/S2',
            'Accessoires': '2 télécommandes incluses',
            'Connectivité': 'WiFi, HDMI x3, USB x2, Optique, AV',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_43_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-50SM',
        'name': 'Smart TV East Point 50" 4K Ultra HD Smart - Décodeur & 2 Télécommandes',
        'slug': 'smart-tv-east-point-50-pouces-4k-ultra-hd-smart',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 170000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV East Point 50" 4K UHD, grand écran connecté WiFi avec décodeur intégré et double télécommande. Garantie 1 an.',
        'description': (
            "Grand écran 50 pouces East Point 4K Ultra HD Smart TV disponible chez Onizouka Shop Bamako !\n\n"
            "Profitez d'un affichage spectaculaire en 4K UHD pour le sport, les films et les séries. "
            "Décodeur intégré et 2 télécommandes fournies d'origine.\n\n"
            "- Dalle 50 pouces 4K Ultra HD ultra fine\n"
            "- Connexion WiFi rapide pour streaming fluide\n"
            "- 2 télécommandes officielles incluses\n"
            "- Garantie 1 an pièces et main d'œuvre"
        ),
        'specifications': {
            'Taille écran': '50 pouces (127 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'Smart TV avec YouTube, Netflix, Prime Video',
            'Décodeur': 'Intégré',
            'Accessoires': '2 télécommandes fournies',
            'Connectique': 'WiFi, HDMI x3, USB x2, RJ45',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_50_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-55SM',
        'name': 'Smart TV East Point 55" 4K Ultra HD Smart - Cadre Fin & Décodeur',
        'slug': 'smart-tv-east-point-55-pouces-4k-ultra-hd-smart',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 215000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV East Point 55" 4K Ultra HD, écran géant frameless, décodeur intégré, 2 télécommandes. Garantie 1 an.',
        'description': (
            "La Smart TV East Point 55 pouces 4K UHD transforme votre salon en salle de cinéma privée !\n\n"
            "Un design élégant sans bordures, une image 4K d'une netteté éclatante et la simplicité de la double télécommande.\n\n"
            "- Écran géant 55 pouces 4K Ultra HD\n"
            "- Décodeur numérique intégré\n"
            "- 2 télécommandes incluses\n"
            "- Garantie 1 an"
        ),
        'specifications': {
            'Taille écran': '55 pouces (140 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Design': 'Frameless (bords ultra-fins)',
            'Décodeur': 'Intégré TNT / Sat',
            'Accessoires': '2 télécommandes',
            'Connectique': 'WiFi, HDMI x3, USB x2, Optique',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_55_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-65SM',
        'name': 'Smart TV East Point 65" 4K Ultra HD Smart - Grand Salon',
        'slug': 'smart-tv-east-point-65-pouces-4k-ultra-hd-smart',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 270000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV East Point 65" 4K UHD, écran immersif 165 cm, 2 télécommandes, décodeur intégré. Garantie 1 an.',
        'description': (
            "Immense écran 65 pouces East Point 4K Ultra HD Smart TV chez Onizouka Shop Bamako !\n\n"
            "Une dalle majestueuse de 165 cm de diagonale avec couleurs éclatantes, HDR et son surround stéréo puissant. "
            "Décodeur intégré et 2 télécommandes incluses.\n\n"
            "- Diagonale spectaculaire 65 pouces 4K UHD\n"
            "- Double télécommande d'origine\n"
            "- Décodeur intégré direct\n"
            "- Garantie officielle 1 an"
        ),
        'specifications': {
            'Taille écran': '65 pouces (165 cm)',
            'Résolution': '4K Ultra HD',
            'Système': 'Smart TV connectée',
            'Décodeur': 'Intégré',
            'Accessoires': '2 télécommandes incluses',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_65_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-65GTV',
        'name': 'Smart TV East Point 65" 4K Google TV Officiel - Commande Vocale',
        'slug': 'smart-tv-east-point-65-pouces-4k-google-tv-officiel',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 305000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'East Point 65" Google TV Officiel avec commande vocale Google Assistant, Play Store, Chromecast intégré, 4K UHD. Garantie 1 an.',
        'description': (
            "Le summum de la technologie intelligente : East Point 65 pouces avec Google TV officiel !\n\n"
            "Accédez à l'ensemble du catalogue Google Play Store, pilotez votre téléviseur à la voix avec Google Assistant "
            "et diffusez instantanément vos vidéos depuis votre smartphone grâce au Chromecast intégré.\n\n"
            "- Système Google TV officiel fluide et personnalisé\n"
            "- Commande vocale intelligente Google Assistant\n"
            "- Écran géant 65 pouces 4K UHD HDR10\n"
            "- 2 télécommandes d'origine fournies\n"
            "- Décodeur intégré et garantie 1 an"
        ),
        'specifications': {
            'Taille écran': '65 pouces (165 cm)',
            'Système d\'exploitation': 'Google TV officiel',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Fonctionnalités': 'Google Assistant vocal, Chromecast, Play Store',
            'Décodeur': 'Intégré',
            'Accessoires': '2 télécommandes incluses',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_65_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-75SM',
        'name': 'Smart TV East Point 75" 4K Ultra HD Smart - Écran Géant Prestige',
        'slug': 'smart-tv-east-point-75-pouces-4k-ultra-hd-smart',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 450000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Écran géant East Point 75 pouces (190 cm) 4K UHD Smart, immersion totale pour salons VIP, décodeur intégré. Garantie 1 an.',
        'description': (
            "Format XXL de prestige : Smart TV East Point 75 pouces 4K Ultra HD chez Onizouka Shop Bamako !\n\n"
            "Près de 2 mètres de diagonale pour un spectacle grandiose. Finition premium en aluminium brossé, "
            "décodeur intégré et 2 télécommandes fournies.\n\n"
            "- Diagonale colossale 75 pouces (190 cm)\n"
            "- Image 4K Ultra HD lumineuse et dynamique\n"
            "- Double télécommande d'origine\n"
            "- Garantie officielle 1 an"
        ),
        'specifications': {
            'Taille écran': '75 pouces (190 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'Smart TV connectée WiFi',
            'Décodeur': 'Intégré',
            'Accessoires': '2 télécommandes incluses',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_75_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },
    {
        'sku': 'ONZ-TV-EP-75GTV',
        'name': 'Smart TV East Point 75" 4K Google TV Officiel - Écran Géant 190 cm',
        'slug': 'smart-tv-east-point-75-pouces-4k-google-tv-officiel',
        'brand': 'East Point',
        'category_slug': 'televiseurs',
        'price': 515000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Prestige ultime : East Point 75" Google TV Officiel 4K, Google Assistant vocal, Chromecast, 2 télécommandes. Garantie 1 an.',
        'description': (
            "L'expérience cinéma absolue à domicile : East Point 75 pouces avec Google TV officiel !\n\n"
            "Toute la puissance de Google TV sur un écran magistral de 190 cm. Commande vocale au micro, "
            "accès illimité à Netflix, Prime Video, YouTube, Disney+ et applications Android TV.\n\n"
            "- Écran géant 75 pouces (190 cm) 4K Ultra HD\n"
            "- Google TV officiel avec Google Assistant vocal\n"
            "- Chromecast intégré pour projection directe\n"
            "- 2 télécommandes d'origine fournies\n"
            "- Décodeur numérique intégré\n"
            "- Garantie officielle 1 an chez Onizouka Shop"
        ),
        'specifications': {
            'Taille écran': '75 pouces (190 cm)',
            'Système d\'exploitation': 'Google TV officiel',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Audio': 'Dolby Audio Stéréo Puissant',
            'Fonctionnalités': 'Google Assistant, Chromecast, Play Store',
            'Décodeur': 'Intégré TNT / Sat',
            'Accessoires': '2 télécommandes incluses',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/ep_75_box.webp',
        'gallery_imgs': ['products/televiseurs/ep_showroom_stack.webp']
    },

    # ==========================================
    # FIZZEN (8 modèles)
    # ==========================================
    {
        'sku': 'ONZ-TV-FZ-32S',
        'name': 'Téléviseur Fizzen 32" Simple LED HD - Cadre Fin',
        'slug': 'televiseur-fizzen-32-pouces-simple-led-hd',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 55000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': False,
        'short_description': 'Téléviseur Fizzen 32 pouces HD, affichage LED haute clarté, ports HDMI et USB multimédia. Garantie 1 an.',
        'description': (
            "Nouvel arrivage Fizzen chez Onizouka Shop Bamako !\n\n"
            "Le téléviseur Fizzen 32 pouces Simple offre une qualité d'image HD remarquable à un prix imbattable à Bamako. "
            "Parfait pour la chambre, le bureau ou le salon familial.\n\n"
            "- Dalle LED HD nette et contrastée\n"
            "- Ports HDMI et USB pour brancher décodeur, clé USB ou console\n"
            "- Faible consommation électrique\n"
            "- Garantie 1 an Onizouka Shop"
        ),
        'specifications': {
            'Taille écran': '32 pouces (80 cm)',
            'Résolution': 'HD 1366 x 768',
            'Connectique': 'HDMI, USB multimédia, Entrée AV',
            'Audio': 'Haut-parleurs stéréo intégrés',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_43_lifestyle.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_gold_android_box.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-32AND',
        'name': 'Smart TV Fizzen 32" Android LED HD - WiFi & Applications',
        'slug': 'smart-tv-fizzen-32-pouces-android-led-hd-wifi',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 70000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV Fizzen 32" sous Android, connectée WiFi avec YouTube, Netflix et téléchargement d\'applications. Garantie 1 an.',
        'description': (
            "La Smart TV Fizzen 32 pouces Android connectée chez Onizouka Shop Bamako !\n\n"
            "Profitez de toute la flexibilité d'Android : YouTube, streaming, réseaux sociaux et jeux. "
            "WiFi rapide et partage d'écran depuis smartphone.\n\n"
            "- Système Android Smart TV intuitif\n"
            "- WiFi intégré et ports HDMI / USB\n"
            "- Garantie 1 an"
        ),
        'specifications': {
            'Taille écran': '32 pouces (80 cm)',
            'Système': 'Android Smart TV',
            'Connectivité': 'WiFi, HDMI, USB, Audio Jack',
            'Applications': 'YouTube, Netflix, Navigateur Web',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_43_lifestyle.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_gold_android_box.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-43AND',
        'name': 'Smart TV Fizzen 43" 4K UHD Android 15 - WiFi & Bluetooth',
        'slug': 'smart-tv-fizzen-43-pouces-4k-uhd-android',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 117000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV Fizzen 43" 4K UHD sous Android, WiFi, Bluetooth, HDMI, USB, design moderne sans bordure. Garantie 1 an.',
        'description': (
            "Élégance et performance : la Smart TV Fizzen 43 pouces 4K UHD chez Onizouka Shop !\n\n"
            "Avec son design moderne ultra-fin, sa résolution 4K éblouissante et sa connectivité WiFi + Bluetooth, "
            "elle offre un divertissement complet pour toute la famille.\n\n"
            "- Résolution 4K Ultra HD\n"
            "- Système Android Smart TV réactif\n"
            "- Connectivité WiFi, Bluetooth, HDMI x3, USB x2\n"
            "- Garantie 1 an constructeur"
        ),
        'specifications': {
            'Taille écran': '43 pouces (108 cm)',
            'Résolution': '4K Ultra HD',
            'Système': 'Android TV',
            'Connectivité': 'WiFi, Bluetooth, HDMI x3, USB x2',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_43_lifestyle.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_frameless_screen.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-50AND',
        'name': 'Smart TV Fizzen 50" 4K UHD Android 14 Gold Series',
        'slug': 'smart-tv-fizzen-50-pouces-4k-uhd-android-gold-series',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 165000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Fizzen Gold Series 50" 4K UHD sous Android 14, processeur ultra-rapide, WiFi, Bluetooth, son surround. Garantie 1 an.',
        'description': (
            "Fizzen Gold Series 50 pouces 4K UHD chez Onizouka Shop Bamako !\n\n"
            "Équipée d'Android 14 et d'un traitement d'image haute dynamique, cette TV offre une fluidité remarquable "
            "pour le sport, le streaming et les jeux vidéo.\n\n"
            "- Série Gold officielle Fizzen\n"
            "- Dalle 50 pouces 4K Ultra HD lumineuse\n"
            "- Système Android 14 dernière génération\n"
            "- Garantie 1 an"
        ),
        'specifications': {
            'Taille écran': '50 pouces (127 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'Android 14 Smart TV',
            'Série': 'Gold Series',
            'Connectivité': 'WiFi, Bluetooth, HDMI, USB',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_gold_android_box.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_frameless_screen.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-55WOS',
        'name': 'Smart TV Fizzen 55" 4K UHD webOS Diamond Series - Magic Remote',
        'slug': 'smart-tv-fizzen-55-pouces-4k-uhd-webos-diamond-series',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 215000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Fizzen Diamond Series 55" 4K UHD sous webOS Hub avec Magic Remote (souris gyroscopique), ThinQ AI et Dolby Audio. Garantie 1 an.',
        'description': (
            "L'excellence technologique : Fizzen 55 pouces webOS Diamond Series chez Onizouka Shop Bamako !\n\n"
            "Le système d'exploitation webOS Hub sous licence officielle vous fait bénéficier de la fameuse Magic Remote "
            "(télécommande pointeur magique type souris d'ordinateur), de l'intelligence artificielle ThinQ et du son Dolby Audio.\n\n"
            "- Système webOS Hub ultra-fluide\n"
            "- Télécommande Magic Remote avec pointeur gyroscopique et micro\n"
            "- Écran 55 pouces 4K Ultra HD QLED / Frameless\n"
            "- Son cinéma Dolby Audio certifié\n"
            "- Garantie officielle 1 an"
        ),
        'specifications': {
            'Taille écran': '55 pouces (140 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'webOS Hub avec ThinQ AI',
            'Télécommande': 'Magic Remote (pointeur gyroscopique & voix)',
            'Audio': 'Dolby Audio Stéréo Premium',
            'Série': 'Diamond Series',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_diamond_webos_box.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_webos_hub.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-65WOS',
        'name': 'Smart TV Fizzen 65" 4K UHD webOS Diamond Series - Magic Remote',
        'slug': 'smart-tv-fizzen-65-pouces-4k-uhd-webos-diamond-series',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 295000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Fizzen Diamond 65" 4K UHD webOS Hub, télécommande Magic Remote gyroscopique, ThinQ AI, écran géant 165 cm. Garantie 1 an.',
        'description': (
            "Majestueuse Smart TV Fizzen 65 pouces webOS Diamond Series chez Onizouka Shop Bamako !\n\n"
            "Profitez d'un écran géant de 165 cm combiné à la rapidité légendaire de webOS et de la Magic Remote. "
            "Navigateur internet complet, Netflix 4K, YouTube 4K, Apple AirPlay 2.\n\n"
            "- Dalle 65 pouces 4K Ultra HD Frameless\n"
            "- Système webOS Hub sous licence officielle\n"
            "- Télécommande Magic Remote incluse\n"
            "- Audio spatial Dolby Audio\n"
            "- Garantie 1 an Onizouka Shop"
        ),
        'specifications': {
            'Taille écran': '65 pouces (165 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'webOS Hub officiel',
            'Télécommande': 'Magic Remote pointeur gyroscopique',
            'Fonctionnalités': 'Apple AirPlay, HomeKit, ThinQ AI',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_diamond_webos_box.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_webos_hub.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-75WOS',
        'name': 'Smart TV Fizzen 75" 4K UHD webOS Diamond Series - Grand Cinéma',
        'slug': 'smart-tv-fizzen-75-pouces-4k-uhd-webos-diamond-series',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 465000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Format prestige Fizzen 75" (190 cm) 4K UHD webOS Hub, Magic Remote, Dolby Audio, design cadre métallique ultra-fin. Garantie 1 an.',
        'description': (
            "Spectacle d'exception : Fizzen 75 pouces webOS Diamond Series chez Onizouka Shop Bamako !\n\n"
            "Une dalle gigantesque de 190 cm avec dalle 4K HDR haute luminosité. Contrôle au pointeur grâce à la Magic Remote. "
            "Idéal pour salons luxueux et salles de conférence.\n\n"
            "- Écran géant 75 pouces (190 cm) 4K UHD\n"
            "- Système webOS avec Magic Remote pointeur magique\n"
            "- Traitement d'image HDR10 & Dolby Audio\n"
            "- Garantie 1 an constructeur"
        ),
        'specifications': {
            'Taille écran': '75 pouces (190 cm)',
            'Résolution': '4K Ultra HD',
            'Système': 'webOS Hub avec ThinQ AI',
            'Télécommande': 'Magic Remote gyroscopique',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_diamond_75_box.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_webos_hub.webp']
    },
    {
        'sku': 'ONZ-TV-FZ-85WOS',
        'name': 'Smart TV Fizzen 85" 4K UHD webOS Diamond Series - Format Colossal 215 cm',
        'slug': 'smart-tv-fizzen-85-pouces-4k-uhd-webos-diamond-series',
        'brand': 'Fizzen',
        'category_slug': 'televiseurs',
        'price': 690000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Le colosse absolu : Fizzen 85 pouces (215 cm de diagonale) 4K UHD webOS Diamond Series, Magic Remote, expérience cinéma totale. Garantie 1 an.',
        'description': (
            "Le sommet du prestige à Bamako : Fizzen 85 pouces 4K UHD webOS Diamond Series chez Onizouka Shop !\n\n"
            "Plus de 2 mètres et 15 centimètres de diagonale ! Une immersion à couper le souffle, une netteté chirurgicale en 4K Ultra HD "
            "et l'ergonomie incomparable du système webOS Hub avec sa télécommande Magic Remote gyroscopique.\n\n"
            "- Diagonale colossale 85 pouces (215 cm)\n"
            "- Système webOS Hub officiel rapide et complet\n"
            "- Télécommande Magic Remote incluse\n"
            "- Dalle QLED / 4K UHD haute luminosité\n"
            "- Garantie officielle 1 an assurée à Bamako"
        ),
        'specifications': {
            'Taille écran': '85 pouces (215 cm)',
            'Résolution': '4K Ultra HD (3840 x 2160)',
            'Système': 'webOS Hub avec ThinQ AI',
            'Télécommande': 'Magic Remote avec pointeur gyroscopique',
            'Audio': 'Dolby Audio surround',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/fizzen_diamond_75_box.webp',
        'gallery_imgs': ['products/televiseurs/fizzen_webos_hub.webp', 'products/televiseurs/fizzen_box_large.webp']
    },

    # ==========================================
    # SAMSUNG AUTHENTIQUE (7 modèles)
    # ==========================================
    {
        'sku': 'ONZ-TV-SAM-UA32H5000',
        'name': 'Smart TV Samsung 32" Full HD Smart (Réf. UA32H5000FUXLY)',
        'slug': 'smart-tv-samsung-32-pouces-full-hd-smart-ua32h5000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 98000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV Samsung authentique 32 pouces Full HD (UA32H5000FUXLY) avec Tizen OS, WiFi, applications officielles et garantie 1 an Samsung.',
        'description': (
            "Authentique Smart TV Samsung 32 pouces chez Onizouka Shop Bamako !\n\n"
            "Modèle original certifié Samsung (Réf. technique : UA32H5000FUXLY). "
            "Bénéficiez de la fidélité des couleurs Samsung Wide Color Enhancer et de l'interface connectée intuitive.\n\n"
            "- Produit 100% authentique Samsung garanti\n"
            "- Qualité d'affichage Full HD nette et éclatante\n"
            "- Système Smart TV Samsung avec YouTube, Netflix\n"
            "- Connectivité WiFi, HDMI, USB\n"
            "- Garantie officielle 1 an constructeur"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA32H5000FUXLY',
            'Taille écran': '32 pouces (80 cm)',
            'Résolution': 'Full HD',
            'Système': 'Samsung Smart TV (Tizen)',
            'Connectique': 'WiFi, HDMI x2, USB, Entrée composante / AV',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_32_stand.webp',
        'gallery_imgs': ['products/televiseurs/samsung_store_stack.webp', 'products/televiseurs/samsung_remote_view.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA43F6000',
        'name': 'Smart TV Samsung 43" Full HD Smart (Réf. UA43F6000FUXLY)',
        'slug': 'smart-tv-samsung-43-pouces-full-hd-smart-ua43f6000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 165000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Smart TV Samsung authentique 43" Full HD (UA43F6000FUXLY) avec macaron officiel Authorised Product, design fin, Tizen OS. Garantie 1 an.',
        'description': (
            "Téléviseur original Samsung 43 pouces Full HD Smart chez Onizouka Shop Bamako !\n\n"
            "Référence constructeur certifiée UA43F6000FUXLY avec macaron bleu d'authenticité Samsung Authorised Product. "
            "Une immersion visuelle et sonore de qualité supérieure signée Samsung.\n\n"
            "- Produit certifié d'origine Samsung\n"
            "- Diagonale 43 pouces (108 cm) Full HD\n"
            "- Smart Hub Samsung avec applications officielles de streaming\n"
            "- Garantie constructeur 1 an avec SAV officiel"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA43F6000FUXLY',
            'Taille écran': '43 pouces (108 cm)',
            'Résolution': 'Full HD 1080p',
            'Système': 'Samsung Smart TV',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_store_stack.webp',
        'gallery_imgs': ['products/televiseurs/samsung_smart_hub.webp', 'products/televiseurs/samsung_remote_view.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA50U8000',
        'name': 'Smart TV Samsung 50" Crystal UHD 4K (Réf. UA50U8000FUXLY)',
        'slug': 'smart-tv-samsung-50-pouces-crystal-uhd-4k-ua50u8000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 235000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Samsung 50 pouces Crystal UHD 4K authentique (UA50U8000FUXLY), processeur Crystal 4K, HDR, design sans bordure. Garantie 1 an Samsung.',
        'description': (
            "Authentique Samsung Crystal UHD 4K 50 pouces chez Onizouka Shop Bamako !\n\n"
            "Référence officielle UA50U8000FUXLY. Le processeur Crystal 4K optimise les couleurs et les contrastes "
            "pour révéler chaque nuance avec une précision cinématographique.\n\n"
            "- Résolution 4K Ultra HD authentique Samsung\n"
            "- Processeur Crystal 4K avec Dynamic Crystal Color\n"
            "- Prise en charge HDR10+ pour contrastes profonds\n"
            "- Système d'exploitation Samsung Tizen OS rapide et sécurisé\n"
            "- Garantie 1 an constructeur"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA50U8000FUXLY',
            'Taille écran': '50 pouces (127 cm)',
            'Résolution': 'Crystal UHD 4K (3840 x 2160)',
            'Processeur': 'Crystal Processor 4K',
            'Système': 'Samsung Tizen OS',
            'Connectivité': 'WiFi, Bluetooth, HDMI x3, USB x2',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_crystal_front.webp',
        'gallery_imgs': ['products/televiseurs/samsung_store_stack.webp', 'products/televiseurs/samsung_living_wall.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA55U8000',
        'name': 'Smart TV Samsung 55" Crystal UHD 4K (Réf. UA55U8000FUXLY)',
        'slug': 'smart-tv-samsung-55-pouces-crystal-uhd-4k-ua55u8000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 289000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Samsung 55" Crystal UHD 4K authentique (UA55U8000FUXLY), design AirSlim ultra-fin, télécommande One Remote, Tizen OS. Garantie 1 an.',
        'description': (
            "Le bestseller mondial Samsung Crystal UHD 55 pouces chez Onizouka Shop Bamako !\n\n"
            "Modèle certifié d'origine UA55U8000FUXLY. Avec son profil AirSlim ultra-fin de moins de 3 cm d'épaisseur, "
            "il s'intègre harmonieusement sur meuble ou en fixation murale.\n\n"
            "- Produit 100% original Samsung\n"
            "- Écran 55 pouces (140 cm) Crystal UHD 4K\n"
            "- Design AirSlim avec gestion discrète des câbles\n"
            "- Tizen OS avec applications Netflix, Prime Video, Apple TV, YouTube en 4K\n"
            "- Garantie 1 an officiel"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA55U8000FUXLY',
            'Taille écran': '55 pouces (140 cm)',
            'Résolution': 'Crystal UHD 4K (3840 x 2160)',
            'Technologie': 'Dynamic Crystal Color & HDR10+',
            'Design': 'AirSlim ultra-fin',
            'Garantie': '1 an'
        },
        'primary_img': 'products/televiseurs/samsung_crystal_uhd_face.webp',
        'gallery_imgs': ['products/televiseurs/samsung_slim_wall.webp', 'products/televiseurs/samsung_store_stack.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA65U8000',
        'name': 'Smart TV Samsung 65" Crystal UHD 4K (Réf. UA65U8000FUXLY)',
        'slug': 'smart-tv-samsung-65-pouces-crystal-uhd-4k-ua65u8000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 390000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Samsung 65" Crystal UHD 4K authentique (UA65U8000FUXLY), écran 163 cm, Dynamic Crystal Color, AirSlim. Garantie 1 an officiel.',
        'description': (
            "Grand spectacle cinématographique : Samsung Crystal UHD 65 pouces authentique chez Onizouka Shop Bamako !\n\n"
            "Référence constructeur officielle UA65U8000FUXLY (163 cm de diagonale visible). "
            "Une image 4K d'une pureté exceptionnelle pour magnifier votre salon de réception.\n\n"
            "- Écran géant 65 pouces 4K UHD authentique Samsung\n"
            "- Processeur Crystal 4K avec upscaling intelligent des sources vidéo\n"
            "- Son OTS Lite (Object Tracking Sound) pour un réalisme sonore captivant\n"
            "- Garantie 1 an assurée par Onizouka Shop"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA65U8000FUXLY',
            'Taille écran': '65 pouces (163 cm)',
            'Résolution': 'Crystal UHD 4K (3840 x 2160)',
            'Son': 'Q-Symphony & OTS Lite',
            'Design': '3-Side Bezelless (sans bordures sur 3 côtés)',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_crystal_uhd_face.webp',
        'gallery_imgs': ['products/televiseurs/samsung_living_wall.webp', 'products/televiseurs/samsung_store_stack.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA75U8000',
        'name': 'Smart TV Samsung 75" Crystal UHD 4K (Réf. UA75U8000FUXLY)',
        'slug': 'smart-tv-samsung-75-pouces-crystal-uhd-4k-ua75u8000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 585000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Samsung 75 pouces Crystal UHD 4K authentique (UA75U8000FUXLY), écran monumental 190 cm, AirSlim, HDR10+, Tizen OS. Garantie 1 an.',
        'description': (
            "Dimension majestueuse de 75 pouces originale Samsung chez Onizouka Shop Bamako !\n\n"
            "Référence constructeur UA75U8000FUXLY. Vivez chaque match de football, film et série avec une intensité émotionnelle inédite "
            "grâce à l'écran de 190 cm et au traitement d'image de pointe Samsung.\n\n"
            "- Écran monumental 75 pouces (190 cm)\n"
            "- Authenticité garantie Samsung avec certificat et garantie officielle\n"
            "- Télécommande One Remote ergonomique\n"
            "- Garantie constructeur 1 an avec assistance technique à Bamako"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA75U8000FUXLY',
            'Taille écran': '75 pouces (190 cm)',
            'Résolution': 'Crystal UHD 4K (3840 x 2160)',
            'Connectivité': 'WiFi, Bluetooth 5.2, HDMI x3 (eARC), USB x2',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_living_wall.webp',
        'gallery_imgs': ['products/televiseurs/samsung_crystal_uhd_face.webp', 'products/televiseurs/samsung_slim_angle.webp']
    },
    {
        'sku': 'ONZ-TV-SAM-UA85U8000',
        'name': 'Smart TV Samsung 85" Crystal UHD 4K (Réf. UA85U8000FUXLY)',
        'slug': 'smart-tv-samsung-85-pouces-crystal-uhd-4k-ua85u8000',
        'brand': 'Samsung',
        'category_slug': 'televiseurs',
        'price': 845000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'short_description': 'Le colosse officiel Samsung : 85 pouces (215 cm de diagonale) Crystal UHD 4K (UA85U8000FUXLY). Le summum du luxe et du divertissement. Garantie 1 an.',
        'description': (
            "Le joyau technologique absolu de Samsung disponible chez Onizouka Shop Bamako !\n\n"
            "Référence originale certifiée UA85U8000FUXLY. Plus de 2,15 mètres de diagonale pour transformer votre salon "
            "en un véritable complexe cinématographique d'exception.\n\n"
            "- Écran géant 85 pouces (215 cm) 4K Ultra HD\n"
            "- Processeur Crystal 4K avec calibrage d'usine de précision\n"
            "- Design AirSlim ultra-épuré\n"
            "- Audio immersif avec technologie Q-Symphony\n"
            "- Garantie 1 an officielle avec service client privilégié à Bamako"
        ),
        'specifications': {
            'Marque': 'Samsung Authentique',
            'Référence constructeur': 'UA85U8000FUXLY',
            'Taille écran': '85 pouces (215 cm)',
            'Résolution': 'Crystal UHD 4K (3840 x 2160)',
            'Processeur': 'Crystal Processor 4K',
            'Garantie': '1 an officiel'
        },
        'primary_img': 'products/televiseurs/samsung_living_wall.webp',
        'gallery_imgs': ['products/televiseurs/samsung_crystal_uhd_face.webp', 'products/televiseurs/samsung_slim_wall.webp']
    },

    # ==========================================
    # ARMOIRES ET MEUBLES DE CHAMBRE (5 modèles)
    # ==========================================
    {
        'sku': 'ONZ-ARM-2P-BOIS',
        'name': 'Armoire de Chambre 2 Portes Bois Marron avec Miroir & Tiroirs',
        'slug': 'armoire-de-chambre-2-portes-bois-marron-miroir-tiroirs',
        'brand': 'Onizouka Confort',
        'category_slug': 'meubles-armoires',
        'price': 130000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'addon_label': 'Montage & Installation à domicile',
        'addon_price': 0,
        'short_description': 'Armoire élégante 2 portes en bois marron avec miroir biseauté, 2 tiroirs extérieurs à serrures et penderie. Livraison et installation incluses à Bamako.',
        'description': (
            "Offrez à votre chambre une touche d'élégance chaleureuse avec l'armoire 2 portes Onizouka Confort !\n\n"
            "Conçue avec des finitions en bois marron texturé résistant, elle intègre un grand miroir central, "
            "deux tiroirs coulissants sécurisés à clé et une spacieuse penderie pour organiser parfaitement vos vêtements.\n\n"
            "SERVICE PREMIUM INCLUS :\n"
            "- Livraison directement à votre domicile à Bamako\n"
            "- Montage et installation complète par nos techniciens qualifiés inclus dans le prix !"
        ),
        'specifications': {
            'Portes': '2 battants avec poignées en aluminium et serrures à clés',
            'Miroir': 'Grand miroir vertical intégré',
            'Tiroirs': '2 tiroirs extérieurs coulissants avec serrures',
            'Rangement intérieur': 'Barre de penderie + étagère supérieure',
            'Matériau': 'Bois d\'ingénierie haute densité avec finition mélamine vernie',
            'Couleur': 'Bois marron veiné noyer',
            'Service': 'Livraison & Installation offertes à Bamako'
        },
        'primary_img': 'products/meubles/armoire_2p_bois_marron.webp',
        'gallery_imgs': []
    },
    {
        'sku': 'ONZ-ARM-3P-BOIS',
        'name': 'Grande Armoire de Chambre 3 Portes Bois Marron avec Miroir Central',
        'slug': 'grande-armoire-de-chambre-3-portes-bois-marron-miroir-central',
        'brand': 'Onizouka Confort',
        'category_slug': 'meubles-armoires',
        'price': 165000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'addon_label': 'Montage & Installation à domicile',
        'addon_price': 0,
        'short_description': 'Grande armoire familiale 3 portes en bois marron avec façade sculptée en damier, miroir central, tiroir et serrure. Livraison et installation incluses à Bamako.',
        'description': (
            "Le grand luxe du rangement pour toute la famille : armoire 3 portes Onizouka Confort !\n\n"
            "Ses façades travaillées avec motifs sculptés en damier et sa teinte marron chaleureuse apportent un cachet exceptionnel à votre chambre. "
            "Elle offre une capacité de rangement colossale avec penderie, multiples étagères, tiroir et serrure sécurisée.\n\n"
            "SERVICE PREMIUM INCLUS :\n"
            "- Livraison à domicile à Bamako\n"
            "- Montage et installation complète assurés par nos menuisiers inclus !"
        ),
        'specifications': {
            'Portes': '3 portes battantes avec panneaux sculptés en damier',
            'Miroir': 'Miroir central vertical de plain-pied',
            'Tiroir': 'Tiroir central avec poignée renforcée',
            'Rangement': 'Grande penderie + étagères de rangement pour linge plié',
            'Sécurité': 'Serrures avec clés d\'origine sur les battants',
            'Couleur': 'Bois chaleureux teck / noyer doré',
            'Service': 'Livraison & Installation offertes à Bamako'
        },
        'primary_img': 'products/meubles/armoire_3p_bois_marron.webp',
        'gallery_imgs': []
    },
    {
        'sku': 'ONZ-ARM-2P-BLANCHE',
        'name': 'Armoire de Chambre Moderne 2 Portes Blanche avec Miroir & Tiroir',
        'slug': 'armoire-de-chambre-moderne-2-portes-blanche-miroir-tiroir',
        'brand': 'Onizouka Confort',
        'category_slug': 'meubles-armoires',
        'price': 130000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'addon_label': 'Montage & Installation à domicile',
        'addon_price': 0,
        'short_description': 'Armoire contemporaine 2 portes blanc pur avec façades matelassées en relief, grand miroir, tiroir et penderie. Livraison et installation incluses à Bamako.',
        'description': (
            "Luminosité et pureté design : l'armoire 2 portes Blanche Onizouka Confort !\n\n"
            "Sa finition blanche éclatante avec motifs en relief texturés illumine votre chambre à coucher. "
            "L'agencement intérieur a été optimisé avec une penderie robuste et des étagères profondes pour vos vêtements.\n\n"
            "SERVICE PREMIUM INCLUS :\n"
            "- Livraison à domicile à Bamako\n"
            "- Montage complet et pose chez vous inclus dans le prix !"
        ),
        'specifications': {
            'Portes': '2 portes avec finition blanche texturée relief',
            'Miroir': 'Miroir rectangulaire vertical',
            'Tiroir': 'Tiroir inférieur avec poignée chromée',
            'Intérieur': 'Barre de penderie suspendue + étagères pour linge',
            'Couleur': 'Blanc pur brillant et mat',
            'Service': 'Livraison & Installation offertes à Bamako'
        },
        'primary_img': 'products/meubles/armoire_2p_blanche_face.webp',
        'gallery_imgs': ['products/meubles/armoire_2p_blanche_interieur.webp']
    },
    {
        'sku': 'ONZ-ARM-2P-ACAJOU',
        'name': 'Armoire de Chambre 2 Portes Rouge Acajou Sculptée avec Miroir',
        'slug': 'armoire-de-chambre-2-portes-rouge-acajou-sculptee-miroir',
        'brand': 'Onizouka Confort',
        'category_slug': 'meubles-armoires',
        'price': 127000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'addon_label': 'Montage & Installation à domicile',
        'addon_price': 0,
        'short_description': 'Armoire raffinée 2 portes rouge acajou verni, panneaux travaillés, miroir vertical, tiroirs et penderie. Livraison et installation incluses à Bamako.',
        'description': (
            "L'élégance du style classique revisité : armoire 2 portes Rouge Acajou Onizouka Confort !\n\n"
            "Sa riche teinte acajou vernie met en valeur le veinage naturel du bois et s'accorde magnifiquement avec tous les intérieurs. "
            "Équipée d'un miroir de courtoisie, d'un espace penderie et de tiroirs extérieurs faciles d'accès.\n\n"
            "SERVICE PREMIUM INCLUS :\n"
            "- Livraison à votre adresse à Bamako\n"
            "- Montage et assemblage sur place sans frais supplémentaires !"
        ),
        'specifications': {
            'Portes': '2 battants avec poignées métalliques',
            'Miroir': 'Miroir frontal avec encadrement mouluré',
            'Tiroirs': 'Tiroirs coulissants avec poignées',
            'Couleur': 'Rouge Acajou / Bois sculpté précieux',
            'Service': 'Livraison & Installation offertes à Bamako'
        },
        'primary_img': 'products/meubles/armoire_2p_rouge_acajou.webp',
        'gallery_imgs': []
    },
    {
        'sku': 'ONZ-ARM-2P-BICOLORE',
        'name': 'Armoire Dressing 2 Portes Bicolore Chêne Clair & Portes Blanches',
        'slug': 'armoire-dressing-2-portes-bicolore-chene-clair-blanc',
        'brand': 'Onizouka Confort',
        'category_slug': 'meubles-armoires',
        'price': 127000,
        'sale_price': None,
        'stock': 10,
        'is_new': True,
        'is_featured': True,
        'addon_label': 'Montage & Installation à domicile',
        'addon_price': 0,
        'short_description': 'Dressing moderne 2 portes style scandinave bicolore chêne naturel et portes blanches, double penderie intérieure et étagère. Livraison et installation incluses à Bamako.',
        'description': (
            "Design scandinave et modernité : armoire dressing 2 portes bicolore Onizouka Confort !\n\n"
            "L'alliance intemporelle du bois chêne clair naturel et des portes blanches satinées confère une élégance zen à votre pièce. "
            "À l'intérieur, découvrez un double compartiment de penderie pour cintres et une grande étagère supérieure pour couvertures et draps.\n\n"
            "SERVICE PREMIUM INCLUS :\n"
            "- Livraison rapide à votre domicile à Bamako\n"
            "- Montage complet et calage par notre équipe de professionnels inclus dans le prix !"
        ),
        'specifications': {
            'Design': 'Style nordique contemporain bicolore',
            'Portes': '2 grandes portes battantes blanc satiné avec longues poignées bois',
            'Structure': 'Caisson robuste en chêne clair naturel',
            'Intérieur': 'Compartiment double penderie avec barres métalliques + étagère linge de lit',
            'Dimensions': 'Environ 80 cm (largeur) x 50 cm (profondeur) x 185 cm (hauteur)',
            'Service': 'Livraison & Installation offertes à Bamako'
        },
        'primary_img': 'products/meubles/armoire_2p_bicolore_fermee.webp',
        'gallery_imgs': [
            'products/meubles/armoire_2p_bicolore_interieur.webp',
            'products/meubles/armoire_2p_bicolore_face.webp',
            'products/meubles/armoire_2p_bicolore_magasin.webp'
        ]
    },
]


def import_products():
    print("\n=== 2. CREATION ET MISE A JOUR DES MARQUES ET CATEGORIES ===")
    with transaction.atomic():
        # Catégorie Téléviseurs
        cat_tv, _ = Category.objects.get_or_create(
            slug='televiseurs',
            defaults={
                'name': 'Téléviseurs & Smart TV',
                'description': 'Téléviseurs 4K UHD, Smart TV Android, webOS, Google TV et écrans LED géants.',
                'is_active': True,
                'parent': None
            }
        )
        if not cat_tv.is_active:
            cat_tv.is_active = True
            cat_tv.save()

        # Catégorie Meubles & Armoires
        cat_meubles, _ = Category.objects.get_or_create(
            slug='meubles-armoires',
            defaults={
                'name': 'Meubles & Armoires',
                'description': 'Armoires de chambre 2 et 3 portes, dressings et mobilier avec livraison et montage offerts à Bamako.',
                'is_active': True,
                'parent': None
            }
        )
        if not cat_meubles.is_active:
            cat_meubles.is_active = True
            cat_meubles.save()

        # Marque Onizouka Confort pour les armoires
        brand_meubles, _ = Brand.objects.get_or_create(
            slug='onizouka-confort',
            defaults={
                'name': 'Onizouka Confort',
                'description': 'Ligne de mobilier, armoires et literie de luxe pour la maison par Onizouka Shop.',
                'is_active': True
            }
        )

        categories_map = {
            'televiseurs': cat_tv,
            'meubles-armoires': cat_meubles
        }

        print("\n=== 3. IMPORTATION DES 29 PRODUITS ===")
        created_count = 0
        updated_count = 0

        for item in PRODUCTS_DATA:
            cat = categories_map[item['category_slug']]
            brand_obj = Brand.objects.filter(name__iexact=item['brand']).first()
            if not brand_obj:
                brand_obj = Brand.objects.filter(slug=slugify(item['brand'])).first()
            if not brand_obj:
                brand_obj = Brand.objects.create(name=item['brand'], slug=slugify(item['brand']))

            # Vérifier si l'image principale existe
            primary_path = MEDIA_ROOT / item['primary_img']
            if not primary_path.exists():
                print(f"  [ATTENTION] Image principale introuvable: {primary_path}")

            # Créer ou mettre à jour le produit
            product, created = Product.objects.update_or_create(
                sku=item['sku'],
                defaults={
                    'name': item['name'],
                    'slug': item['slug'],
                    'category': cat,
                    'brand': brand_obj,
                    'price': item['price'],
                    'sale_price': item.get('sale_price'),
                    'stock': item.get('stock', 10),
                    'is_active': True,
                    'is_new': item.get('is_new', True),
                    'is_featured': item.get('is_featured', False),
                    'status': Product.Status.ACTIVE,
                    'short_description': item['short_description'],
                    'description': item['description'],
                    'specifications': item.get('specifications', {}),
                    'addon_label': item.get('addon_label', ''),
                    'addon_price': item.get('addon_price', 0),
                }
            )

            if created:
                created_count += 1
                action_str = "CREE"
            else:
                updated_count += 1
                action_str = "MAJ"

            # Associer les images dans ProductImage
            # 1. Image principale
            ProductImage.objects.filter(product=product).delete() # Réinitialisation propre des images
            ProductImage.objects.create(
                product=product,
                image=item['primary_img'],
                alt_text=f"{product.name} - Vue principale",
                is_primary=True,
                order=0
            )

            # 2. Images de galerie
            for idx, g_img in enumerate(item.get('gallery_imgs', []), start=1):
                if (MEDIA_ROOT / g_img).exists():
                    ProductImage.objects.create(
                        product=product,
                        image=g_img,
                        alt_text=f"{product.name} - Vue secondaire {idx}",
                        is_primary=False,
                        order=idx
                    )

            print(f"  [{action_str}] {product.sku} - {product.name[:45]}... | {product.price:,} FCFA | Images: {1 + len(item.get('gallery_imgs', []))}")

        print(f"\nTerminé avec succès ! Total créés: {created_count}, Total mis à jour: {updated_count}")
        print(f"Nombre total de produits en base: {Product.objects.count()}")

if __name__ == '__main__':
    process_images()
    import_products()
