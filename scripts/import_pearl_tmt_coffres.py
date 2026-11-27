"""
Import des Congélateurs Horizontaux Pearl et TMT pour Onizuka Shop
- Pearl 375 Litres (2 battants + vitres coulissantes) : 369 000 FCFA
- TMT 200 Litres (1 battant + vitres coulissantes) : 215 000 FCFA
- TMT 288 Litres (1 battant + vitres coulissantes) : 272 000 FCFA
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

from PIL import Image
from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

MEDIA_ROOT = BASE_DIR / 'media'
DEST_DIR = MEDIA_ROOT / 'products' / 'congelateurs_coffres'
DEST_DIR.mkdir(parents=True, exist_ok=True)

USER_UPLOADED = Path('C:/Users/a/.gemini/antigravity/brain/507b0a9b-c11c-4a9e-a9ab-0b97eff9541e/.user_uploaded')

def convert_to_webp(src_path: Path, dest_path: Path):
    with Image.open(src_path) as im:
        rgb_im = im.convert('RGB')
        rgb_im.save(dest_path, 'WEBP', quality=88, method=6)
    print(f" -> WebP généré: {dest_path.name} ({dest_path.stat().st_size // 1024} Ko)")

NEW_PRODUCTS = [
    {
        'brand_name': 'Pearl',
        'brand_slug': 'pearl',
        'brand_desc': 'Fabricant réputé d\'appareils électroménagers haute performance et économes en énergie.',
        'sku': 'ONZ-PEARL-CH-375L',
        'name': 'Congélateur Coffre Horizontal Pearl 375 Litres - 2 Battants & Vitres Coulissantes',
        'litres': 375,
        'price': 369000,
        'description': (
            "Congélateur coffre horizontal haut de gamme Pearl d'une capacité nette de 375 litres avec technologie « Retain Freshness All Day ». "
            "Équipé d'une double ouverture à 2 battants indépendants doublée de vitres coulissantes transparentes intérieures sur les deux compartiments. "
            "Cette triple barrière thermique empêche la remontée de température lors des ouvertures répétées et conserve le froid jusqu'à 48h "
            "en cas de coupure de courant à Bamako. Dispose d'un compresseur tropicalisé ultra-silencieux, d'un panier suspendu pour accès rapide, "
            "d'un double éclairage intérieur et d'un panneau de contrôle en façade avec voyants d'alimentation. Finition soignée gris métallisé "
            "anti-rayures. Parfait pour les commerces, restaurants et grandes familles. Garanti Onizuka Shop au Grand Marché de Bamako (Dibidani)."
        ),
        'specs': {
            'Capacité brute / nette': '375 Litres',
            'Marque': 'Pearl (Quality Our Priority)',
            'Technologie': 'Retain Freshness All Day (Conservation prolongée)',
            'Type': 'Congélateur coffre horizontal double battant avec vitres thermiques',
            'Portes / Battants': '2 battants indépendants étanches',
            'Isolation intérieure': 'Double baie vitrée coulissante transparente',
            'Sécurité': 'Serrure intégrée',
            'Rangement': 'Panier métallique suspendu amovible',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd spécial Bamako)',
            'Couleur': 'Gris métallisé premium',
            'Contrôle': 'Thermostat réglable frontal avec témoins lumineux',
            'Vidange': 'Bouchon de dégivrage en façade',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795792229961_105a3979.jpg', 'dest': 'pearl_coffre_375l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795792244574_7ea403ac.jpg', 'dest': 'pearl_coffre_375l_ouvert.webp', 'is_primary': False},
            {'src': USER_UPLOADED / 'media_1795792222428_486acce2.jpg', 'dest': 'pearl_coffre_375l_interieur_badge.webp', 'is_primary': False},
        ]
    },
    {
        'brand_name': 'TMT',
        'brand_slug': 'tmt',
        'brand_desc': 'Marque spécialisée en réfrigération commerciale et domestique avec vitres coulissantes isolantes.',
        'sku': 'ONZ-TMT-CH-200L',
        'name': 'Congélateur Coffre Horizontal TMT 200 Litres - Vitres Coulissantes Intérieures',
        'litres': 200,
        'price': 215000,
        'description': (
            "Congélateur coffre horizontal TMT 200 litres avec compresseur puissant garantissant une congélation profonde rapide jusqu'à -18°C. "
            "Son couvercle supérieur s'ouvre sur un système de vitres coulissantes transparentes montées sur glissières étanches qui emprisonnent "
            "le froid à l'intérieur. Idéal pour conserver viandes fraîches, poissons, glaces et boissons sans gaspillage énergétique. "
            "Équipé d'un éclairage intérieur automatique, d'un panier métallique pour ranger les petits sachets, d'une serrure à clé et d'un "
            "thermostat précis en façade. Carrosserie robuste en acier laqué gris anti-rouille. Disponible immédiatement au showroom Dibidani."
        ),
        'specs': {
            'Capacité brute / nette': '200 Litres',
            'Marque': 'TMT',
            'Performance frigorifique': 'Congélation profonde rapide -18°C',
            'Type': 'Congélateur coffre horizontal avec vitres coulissantes',
            'Porte principale': '1 large battant avec éclairage intégré',
            'Double isolation': 'Vitres coulissantes intérieures transparentes',
            'Sécurité': 'Serrure de fermeture à clé',
            'Rangement': 'Panier métallique suspendu',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé Bamako)',
            'Couleur': 'Gris Silver métallisé',
            'Vidange': 'Évacuation frontale pour nettoyage',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795792271714_b032a4bd.jpg', 'dest': 'tmt_coffre_200l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795792261902_eb4542bf.jpg', 'dest': 'tmt_coffre_200l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'brand_name': 'TMT',
        'brand_slug': 'tmt',
        'brand_desc': 'Marque spécialisée en réfrigération commerciale et domestique avec vitres coulissantes isolantes.',
        'sku': 'ONZ-TMT-CH-288L',
        'name': 'Congélateur Coffre Horizontal TMT 288 Litres - Vitres Coulissantes Intérieures',
        'litres': 288,
        'price': 272000,
        'description': (
            "Congélateur coffre horizontal TMT 288 litres grand volume, associant capacité de chargement généreuse et compresseur tropicalisé "
            "haute endurance. Intègre des doubles vitres coulissantes intérieures transparentes permettant de visualiser le contenu et de choisir "
            "ses articles sans faire monter la température de la cuve. Permet d'atteindre rapidement -18°C pour une conservation saine des aliments "
            "sur le long terme. Muni d'un éclairage intérieur sous le battant, d'un panier suspendu amovible, d'un verrou à clé et d'un bouchon "
            "de vidange frontal pour un dégivrage propre et sans effort. Livrable partout à Bamako ou retrait direct à notre boutique de Dibidani."
        ),
        'specs': {
            'Capacité brute / nette': '288 Litres',
            'Marque': 'TMT',
            'Performance frigorifique': 'Congélation rapide -18°C',
            'Type': 'Congélateur coffre horizontal grand format avec vitres coulissantes',
            'Porte principale': '1 grand battant avec éclairage intégré',
            'Système thermique': 'Vitres coulissantes intérieures transparentes',
            'Sécurité': 'Serrure avec clé de verrouillage',
            'Rangement': 'Panier métallique pour accès rapide',
            'Cuve intérieure': 'Aluminium martelé résistant à la corrosion',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris métallisé premium',
            'Thermostat': 'Réglable en façade avec témoins lumineux',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795792296233_e881378b.jpg', 'dest': 'tmt_coffre_288l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795792290642_815ef96f.jpg', 'dest': 'tmt_coffre_288l_ouvert.webp', 'is_primary': False},
        ]
    }
]

def run():
    print("=== DÉBUT IMPORT DES CONGÉLATEURS PEARL ET TMT ===")
    cat = Category.objects.get(slug='congelateurs-horizontaux')
    
    for item in NEW_PRODUCTS:
        brand, _ = Brand.objects.get_or_create(
            slug=item['brand_slug'],
            defaults={
                'name': item['brand_name'],
                'description': item['brand_desc'],
                'is_active': True,
            }
        )
        
        sku = item['sku']
        name = item['name']
        price = item['price']
        desc = item['description']
        specs = item['specs']
        
        print(f"\nTraitement {sku} - {name} ({price:,} FCFA)...")
        
        slug = slugify(f"congelateur-horizontal-{item['brand_slug']}-{item['litres']}l")
        product, created = Product.objects.update_or_create(
            sku=sku,
            defaults={
                'name': name,
                'slug': slug,
                'brand': brand,
                'category': cat,
                'price': price,
                'description': desc,
                'specifications': specs,
                'stock': 10,
                'track_stock': True,
                'status': Product.Status.ACTIVE,
                'is_active': True,
                'is_featured': True if item['litres'] == 375 else False,
            }
        )
        print(f" -> Produit {'Créé' if created else 'Mis à jour'} (ID={product.id})")
        
        ProductImage.objects.filter(product=product).delete()
        for idx, img_info in enumerate(item['images']):
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
                    order=idx,
                    is_primary=img_info['is_primary']
                )
            else:
                print(f" [ATTENTION] Fichier introuvable: {src}")
                
        print(f" -> Images associées pour {sku}")
        
    print("\n=== IMPORT TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue : {Product.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    run()
