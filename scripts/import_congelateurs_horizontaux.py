"""
Import des 7 Congélateurs Horizontaux (Coffres) Fizzen pour Onizuka Shop
- 110 Litres : 132 000 FCFA
- 160 Litres : 177 000 FCFA
- 210 Litres : 205 000 FCFA
- 270 Litres : 232 000 FCFA
- 350 Litres : 274 000 FCFA
- 430 Litres : 374 000 FCFA (2 battants)
- 550 Litres : 447 000 FCFA (2 battants)
"""
import os
import shutil
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

from PIL import Image
from django.core.files import File
from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

MEDIA_ROOT = BASE_DIR / 'media'
DEST_DIR = MEDIA_ROOT / 'products' / 'congelateurs_coffres'
DEST_DIR.mkdir(parents=True, exist_ok=True)

USER_UPLOADED = Path('C:/Users/a/.gemini/antigravity/brain/507b0a9b-c11c-4a9e-a9ab-0b97eff9541e/.user_uploaded')

PRODUCTS_DATA = [
    {
        'sku': 'ONZ-FZ-CH-110L',
        'name': 'Congélateur Coffre Horizontal Fizzen 110 Litres Compact',
        'litres': 110,
        'model': 'FZ_AC-110_CH/FR',
        'price': 132000,
        'description': (
            "Congélateur coffre horizontal Fizzen d'une capacité nette de 110 litres, compact et extrêmement économique. "
            "Parfait pour les petits commerces, les boutiques de quartier, les bureaux ou les ménages à Bamako recherchant "
            "une congélation puissante sans encombrer l'espace. Doté d'une poignée ergonomique avec serrure à clé pour sécuriser "
            "vos denrées, d'un panier suspendu métallique amovible pour organiser les petits articles, et d'un thermostat réglable "
            "en façade. Moteur tropicalisé conçu pour résister aux climats chauds avec une isolation thermique renforcée assurant "
            "le maintien du froid lors des coupures d'électricité. Disponible au Showroom Onizuka Shop au Grand Marché de Bamako (Dibidani)."
        ),
        'specs': {
            'Capacité brute / nette': '110 Litres',
            'Type': 'Congélateur coffre horizontal (Chest Freezer)',
            'Porte / Battant': '1 grand battant relevable avec poignée',
            'Sécurité': 'Serrure intégrée avec double clé',
            'Rangement': '1 panier panier métallique suspendu amovible',
            'Alimentation': '220V - 240V / 50Hz',
            'Gaz réfrigérant': 'R600a écologique',
            'Classe climatique': 'T (Tropicalisé spécial Bamako / Afrique de l\'Ouest)',
            'Couleur': 'Gris Silver métallisé anti-corrosion',
            'Contrôle': 'Thermostat réglable en façade avec voyants lumineux',
            'Vidange': 'Bouchon de dégivrage frontal pratique',
        },
        'doors': 1,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791229776_2b3b5111.jpg', 'dest': 'fizzen_coffre_110l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791246967_5d4cdcf7.jpg', 'dest': 'fizzen_coffre_110l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-160L',
        'name': 'Congélateur Coffre Horizontal Fizzen 160 Litres',
        'litres': 160,
        'model': 'FZ_AC-160_CH/FR',
        'price': 177000,
        'description': (
            "Congélateur horizontal coffre Fizzen 160 litres (modèle FZ_AC-160_CH/FR) alliant robustesse et haute efficacité énergétique. "
            "Équipé d'un compresseur tropicalisé ultra-performant assurant une descente rapide en température jusqu'à -18°C. "
            "Sa carrosserie en acier traité gris métallisé offre une excellente résistance contre l'oxydation. Comprend une poignée de verrouillage "
            "avec serrure à clé, un panier intérieur amovible, un thermostat réglable précis et des roulettes de déplacement faciles. "
            "Idéal pour conserver viandes, poissons, boissons et sachets d'eau fraîche avec une faible consommation sur le réseau EDM. "
            "Garanti et disponible en retrait immédiat à Dibidani ou en livraison partout à Bamako."
        ),
        'specs': {
            'Capacité brute / nette': '160 Litres',
            'Modèle constructeur': 'FZ_AC-160_CH/FR',
            'Type': 'Congélateur coffre horizontal (Chest Freezer)',
            'Porte / Battant': '1 grand battant avec poignée robuste',
            'Sécurité': 'Serrure avec clé de verrouillage',
            'Rangement': 'Panier intérieur métallique inclus',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris métallisé premium',
            'Contrôle': 'Thermostat mécanique en façade',
            'Vidange': 'Évacuation frontale pour nettoyage aisé',
        },
        'doors': 1,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791264931_acccc592.jpg', 'dest': 'fizzen_coffre_160l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791272190_f86019ce.jpg', 'dest': 'fizzen_coffre_160l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-210L',
        'name': 'Congélateur Coffre Horizontal Fizzen 210 Litres',
        'litres': 210,
        'model': 'FZ_AC-210_CH/FR',
        'price': 205000,
        'description': (
            "Congélateur coffre horizontal Fizzen 210 litres (modèle officiel FZ_AC-210_CH/FR), le format familial et commercial par excellence. "
            "Offre un volume intérieur spacieux pour stocker d'importantes réserves alimentaires avec un encombrement maîtrisé au sol. "
            "Son compresseur renforcé pour l'Afrique de l'Ouest délivre un froid puissant et constant même lors des fortes chaleurs estivales. "
            "Muni d'un battant étanche avec joint thermique antibactérien démontable, d'une serrure à clé de sécurité, d'un panier métallique suspendu "
            "et d'un orifice de vidange avant pour un dégivrage sans effort. Retrait au magasin Dibidani ou livraison à domicile sécurisée."
        ),
        'specs': {
            'Capacité brute / nette': '210 Litres',
            'Modèle constructeur': 'FZ_AC-210_CH/FR',
            'Type': 'Congélateur coffre horizontal (Chest Freezer)',
            'Porte / Battant': '1 grand battant robuste',
            'Sécurité': 'Serrure à clé intégrée',
            'Rangement': 'Panier métallique pour accès rapide',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé spécial Bamako)',
            'Couleur': 'Gris Silver métallisé',
            'Thermostat': 'Réglable multi-positions en façade',
            'Vidange': 'Bouchon de purge en façade',
        },
        'doors': 1,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791315173_0b15508d.jpg', 'dest': 'fizzen_coffre_210l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791306810_ac6ba8e3.jpg', 'dest': 'fizzen_coffre_210l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-270L',
        'name': 'Congélateur Coffre Horizontal Fizzen 270 Litres Grand Volume',
        'litres': 270,
        'model': 'FZ_AC-270_CH/FR',
        'price': 232000,
        'description': (
            "Congélateur coffre horizontal Fizzen 270 litres (modèle FZ_AC-270_CH/FR) offrant un confort de stockage optimal pour les familles "
            "nombreuses, restaurants, gargotes et commerces d'alimentation générale à Bamako. Sa cuve en aluminium gaufré martelé optimise "
            "la conduction thermique pour une surgélation uniforme de tous vos produits. Intègre une poignée extérieure renforcée avec serrure, "
            "un panier de rangement compartimenté, des roulettes pour faciliter l'installation et un système d'isolation haute densité conservant "
            "la température intérieure durant de longues heures sans électricité. Pièce d'origine Fizzen avec garantie boutique officielle."
        ),
        'specs': {
            'Capacité brute / nette': '270 Litres',
            'Modèle constructeur': 'FZ_AC-270_CH/FR',
            'Type': 'Congélateur coffre horizontal grand format',
            'Porte / Battant': '1 grand battant avec poignée renforcée',
            'Sécurité': 'Serrure avec clé de sécurité',
            'Rangement': 'Panier métallique suspendu',
            'Cuve intérieure': 'Aluminium martelé haute conductivité thermique',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris Silver élégant',
            'Thermostat': 'Contrôle précis avec indicateurs LED',
        },
        'doors': 1,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791344888_376a4ef2.jpg', 'dest': 'fizzen_coffre_270l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791335944_4a7c1ebe.jpg', 'dest': 'fizzen_coffre_270l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-350L',
        'name': 'Congélateur Coffre Horizontal Fizzen 350 Litres',
        'litres': 350,
        'model': 'FZ_AC-350_CH/FR',
        'price': 274000,
        'description': (
            "Congélateur coffre horizontal Fizzen 350 litres haute capacité, parfait pour les professionnels de la restauration, les épiceries, "
            "les traiteurs et les ménages exigeants. Conçu avec des parois épaissies assurant une isolation frigorifique de tout premier ordre face "
            "aux aléas électriques. Son compresseur puissant assure un débit de congélation impressionnant pour préserver les qualités nutritives "
            "des aliments les plus fragiles. Présente un panneau de contrôle clair en façade, un système d'évacuation d'eau rapide, une fermeture "
            "à clé sécurisée et des finitions soignées en acier laqué gris. Disponible au Grand Marché de Bamako avec service après-vente dédié."
        ),
        'specs': {
            'Capacité brute / nette': '350 Litres',
            'Type': 'Congélateur coffre horizontal grande capacité',
            'Porte / Battant': '1 large battant avec charnières équilibrées',
            'Sécurité': 'Serrure de sécurité à clé',
            'Rangement': 'Panier amovible inclus',
            'Cuve': 'Revêtement intérieur facile à nettoyer',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris métallisé',
            'Thermostat': 'Réglable en façade',
            'Mobilité': 'Pieds / roulettes robustes',
        },
        'doors': 1,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791364288_a3b9118c.jpg', 'dest': 'fizzen_coffre_350l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791371903_836343c7.jpg', 'dest': 'fizzen_coffre_350l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-430L',
        'name': 'Congélateur Coffre Horizontal Fizzen 430 Litres - 2 Battants Indépendants',
        'litres': 430,
        'model': 'FZ_AC-430_CH/FR',
        'price': 374000,
        'description': (
            "Congélateur coffre professionnel Fizzen 430 litres (modèle FZ_AC-430_CH/FR) doté d'une conception ingénieuse à deux battants indépendants. "
            "Cette ouverture séparée permet d'accéder à une section sans déperdition d'air froid dans le reste de la cuve, générant d'importantes "
            "économies d'énergie électrique. Idéal pour les supérettes, bars, hôtels, boucheries et commerces de gros à Bamako. "
            "Chaque battant dispose de sa propre poignée avec serrure à clé individuelle. Intègre un compresseur tropicalisé surdimensionné "
            "pour un refroidissement ultrarapide, un panier de tri et un éclairage intérieur pratique. Vendu avec garantie officielle Onizuka Shop."
        ),
        'specs': {
            'Capacité brute / nette': '430 Litres',
            'Modèle constructeur': 'FZ_AC-430_CH/FR',
            'Type': 'Congélateur coffre horizontal double porte (2 battants)',
            'Portes / Battants': '2 grands battants indépendants étanches',
            'Sécurité': 'Double serrure à clé indépendante',
            'Rangement': 'Panier suspendu et compartiments spacieux',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé usage intensif)',
            'Couleur': 'Gris Silver métallisé anti-traces',
            'Contrôle': 'Thermostat réglable frontal avec témoins de contrôle',
            'Vidange': 'Bouchon de dégivrage frontal',
        },
        'doors': 2,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791396341_36c07727.jpg', 'dest': 'fizzen_coffre_430l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791390973_554cbe2f.jpg', 'dest': 'fizzen_coffre_430l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-FZ-CH-550L',
        'name': 'Congélateur Coffre Horizontal Fizzen 550 Litres PRO - 2 Battants Géants',
        'litres': 550,
        'model': 'FZ_AC-550_CH/FR',
        'price': 447000,
        'description': (
            "Le fleuron des congélateurs horizontaux Fizzen : modèle géant 550 litres à deux battants indépendants conçu pour les besoins "
            "professionnels intensifs et les grandes structures commerciales. Sa cuve immense permet d'entreposer des volumes massifs de vivres, "
            "carcasses, poissons, boissons et blocs de glace. Équipé d'un groupe moteur à haute endurance tropicalisée spécialement calibré "
            "pour affronter les températures caniculaires sans surchauffe. Double système de fermeture à clé, éclairage intérieur LED automatique, "
            "panier suspendu et isolation renforcée garantissant un maintien au froid prolongé. Le meilleur rapport volume / robustesse / prix "
            "à Bamako, garanti et suivi par notre service technique à Dibidani."
        ),
        'specs': {
            'Capacité brute / nette': '550 Litres',
            'Modèle constructeur': 'FZ_AC-550_CH/FR',
            'Type': 'Congélateur coffre professionnel 2 battants grand format',
            'Portes / Battants': '2 très grands battants indépendants',
            'Sécurité': 'Double verrouillage à clé pour chaque battant',
            'Éclairage': 'Éclairage intérieur intégré',
            'Rangement': 'Grand panier suspendu et cuve compartimentable',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd)',
            'Couleur': 'Gris métallisé premium haute résistance',
            'Thermostat': 'Contrôle électronique / mécanique robuste en façade',
            'Vidange': 'Purge de dégivrage intégrée',
        },
        'doors': 2,
        'images': [
            {'src': USER_UPLOADED / 'media_1795791424159_c54f6334.jpg', 'dest': 'fizzen_coffre_550l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791418386_dc2dbdd9.jpg', 'dest': 'fizzen_coffre_550l_ouvert.webp', 'is_primary': False},
        ]
    },
]


def convert_to_webp(src_path: Path, dest_path: Path):
    """Convertit une image en WebP haute fidélité optimisée pour le web."""
    with Image.open(src_path) as im:
        rgb_im = im.convert('RGB')
        rgb_im.save(dest_path, 'WEBP', quality=88, method=6)
    print(f" -> WebP généré: {dest_path.name} ({dest_path.stat().st_size // 1024} Ko)")


def run():
    print("=== DÉBUT IMPORT DES 7 CONGÉLATEURS COFFRES FIZZEN ===")

    # 1. Marque Fizzen
    brand, _ = Brand.objects.get_or_create(
        slug='fizzen',
        defaults={'name': 'Fizzen', 'description': 'Marque d\'appareils électroménagers et solaires de haute qualité pour l\'Afrique.', 'is_active': True}
    )

    # 2. Catégorie Parent : Réfrigérateurs & Congélateurs
    parent_cat, _ = Category.objects.get_or_create(
        slug='refrigerateurs-congelateurs',
        defaults={'name': 'Réfrigérateurs & Congélateurs', 'order': 1, 'is_active': True}
    )

    # 3. Sous-Catégorie : Congélateurs Horizontaux (Coffres)
    sub_cat, _ = Category.objects.get_or_create(
        slug='congelateurs-horizontaux',
        defaults={
            'name': 'Congélateurs Horizontaux (Coffres)',
            'parent': parent_cat,
            'order': 1,
            'is_active': True,
            'description': 'Sélection de congélateurs coffres horizontaux Fizzen ultra-performants, économiques et tropicalisés.'
        }
    )
    if sub_cat.parent != parent_cat:
        sub_cat.parent = parent_cat
        sub_cat.save(update_fields=['parent'])

    print(f"Catégorie prête : {sub_cat.name} (Parent: {parent_cat.name})")

    # 4. Traitement de chaque produit
    for item in PRODUCTS_DATA:
        sku = item['sku']
        name = item['name']
        price = item['price']
        desc = item['description']
        specs = item['specs']

        print(f"\nTraitement {sku} - {name} ({price:,} FCFA)...")

        slug = slugify(f"congelateur-horizontal-fizzen-{item['litres']}l")
        product, created = Product.objects.update_or_create(
            sku=sku,
            defaults={
                'name': name,
                'slug': slug,
                'brand': brand,
                'category': sub_cat,
                'price': price,
                'description': desc,
                'specifications': specs,
                'stock': 10,
                'track_stock': True,
                'status': Product.Status.ACTIVE,
                'is_active': True,
                'is_featured': True if item['litres'] in (210, 430) else False,
            }
        )
        action_str = "Créé" if created else "Mis à jour"
        print(f" -> Produit {action_str} (ID={product.id})")

        # Gestion des photos
        # Supprimer les anciennes images secondaires si mise à jour
        ProductImage.objects.filter(product=product).delete()

        first_image_rel = None
        for img_info in item['images']:
            src = img_info['src']
            dest_name = img_info['dest']
            dest_file = DEST_DIR / dest_name

            if src.exists():
                convert_to_webp(src, dest_file)
                rel_path = f"products/congelateurs_coffres/{dest_name}"

                ProductImage.objects.create(
                    product=product,
                    image=rel_path,
                    alt_text=f"{product.name} - Vue réelle Dibidani",
                    order=0 if img_info['is_primary'] else 1,
                    is_primary=img_info['is_primary']
                )
            else:
                print(f" [ATTENTION] Fichier introuvable: {src}")

        print(f" -> Images associées pour {sku}")

    print("\n=== IMPORT TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue: {Product.objects.filter(is_active=True).count()}")


if __name__ == '__main__':
    run()
