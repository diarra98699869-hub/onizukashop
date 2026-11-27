"""
Import des Congélateurs Horizontaux Roch pour Onizuka Shop
- Roch 550 Litres PRO (2 battants) : 415 000 FCFA
- Roch 316 Litres (1 battant + vitre coulissante) : 299 000 FCFA
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

ROCH_PRODUCTS = [
    {
        'sku': 'ONZ-ROCH-CH-316L',
        'name': 'Congélateur Coffre Horizontal Roch 316 Litres - Vitres Coulissantes Intérieures',
        'litres': 316,
        'price': 299000,
        'description': (
            "Congélateur coffre horizontal Roch 316 litres de nouvelle génération équipé de vitres coulissantes transparentes intérieures. "
            "Cette conception innovante empêche la déperdition d'air froid lors de l'ouverture du couvercle principal, garantissant une conservation "
            "maximale de vos vivres et d'importantes économies d'électricité à Bamako. Doté de la technologie exclusive « Roch Fast Freezing » "
            "pour une congélation à cœur ultra-rapide des viandes, poissons et jus de fruits. Comprend un éclairage LED intégré dans le couvercle, "
            "un panier métallique suspendu, une serrure de sécurité avec clé et un thermostat réglable en façade. Cuve en aluminium gaufré martelé "
            "anti-corrosion. Moteur tropicalisé conçu pour endurer les fortes chaleurs. Disponible au Showroom Onizuka Shop au Grand Marché de Bamako (Dibidani)."
        ),
        'specs': {
            'Capacité brute / nette': '316 Litres',
            'Marque': 'Roch',
            'Technologie': 'Roch Fast Freezing (Surgélation rapide)',
            'Type': 'Congélateur coffre horizontal avec double isolation',
            'Isolation spéciale': 'Portes vitrées coulissantes intérieures transparentes',
            'Porte principale': '1 large battant avec poignées intégrées',
            'Sécurité': 'Serrure à clé intégrée',
            'Éclairage': 'Éclairage LED automatique sous le couvercle',
            'Rangement': 'Panier métallique suspendu amovible',
            'Cuve intérieure': 'Aluminium gaufré martelé haute conductivité',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris métallisé premium',
            'Vidange': 'Bouchon de dégivrage frontal',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795791994404_551ad0ac.jpg', 'dest': 'roch_coffre_316l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795792002391_0cb56706.jpg', 'dest': 'roch_coffre_316l_ouvert.webp', 'is_primary': False},
        ]
    },
    {
        'sku': 'ONZ-ROCH-CH-550L',
        'name': 'Congélateur Coffre Horizontal Roch 550 Litres PRO - 2 Battants Fast Freezing',
        'litres': 550,
        'price': 415000,
        'description': (
            "Congélateur coffre horizontal professionnel Roch d'une grande capacité de 550 litres, conçu spécialement pour un usage "
            "intensif et commercial à Bamako. Doté de la technologie exclusive « ROCH Fast Freezing » assurant une descente ultrarapide "
            "en température pour préserver la fraîcheur absolue des viandes, poissons, glaces, volailles et boissons. Équipé d'une double "
            "porte à deux battants indépendants limitant la déperdition d'air froid, d'un double éclairage intérieur LED automatique, "
            "de 2 grands paniers suspendus amovibles et de serrures à clé de sécurité. Sa cuve interne en aluminium martelé gaufré garantit "
            "une répartition optimale du froid et une protection totale contre la corrosion. Tropicalisé lourd pour résister aux fortes chaleurs "
            "sans surconsommation électrique. Disponible au Grand Marché de Bamako avec garantie officielle Onizuka Shop."
        ),
        'specs': {
            'Capacité brute / nette': '550 Litres',
            'Marque': 'Roch',
            'Technologie': 'Roch Fast Freezing (Surgélation ultra-rapide)',
            'Type': 'Congélateur coffre professionnel double porte (2 battants)',
            'Portes / Battants': '2 grands battants indépendants avec poignées intégrées',
            'Sécurité': 'Double serrure à clé indépendante',
            'Éclairage': 'Double éclairage LED automatique intégré aux couvercles',
            'Rangement': '2 grands paniers métalliques suspendus amovibles',
            'Cuve intérieure': 'Aluminium gaufré martelé haute conduction thermique',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd spécial Bamako)',
            'Couleur': 'Gris Silver métallisé haute durabilité',
            'Vidange': 'Bouchon de vidange frontal pour dégivrage rapide',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795791951332_fad64636.jpg', 'dest': 'roch_coffre_550l_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795791956985_c9fc803d.jpg', 'dest': 'roch_coffre_550l_ouvert.webp', 'is_primary': False},
        ]
    }
]

def run():
    print("=== DÉBUT IMPORT DES CONGÉLATEURS COFFRES ROCH ===")
    
    brand = Brand.objects.get(slug='roch')
    cat = Category.objects.get(slug='congelateurs-horizontaux')
    
    for item in ROCH_PRODUCTS:
        sku = item['sku']
        name = item['name']
        price = item['price']
        desc = item['description']
        specs = item['specs']
        
        print(f"\nTraitement {sku} - {name} ({price:,} FCFA)...")
        
        slug = slugify(f"congelateur-horizontal-roch-{item['litres']}l")
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
                'is_featured': True if item['litres'] == 550 else False,
            }
        )
        print(f" -> Produit {'Créé' if created else 'Mis à jour'} (ID={product.id})")
        
        ProductImage.objects.filter(product=product).delete()
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
        
    print("\n=== IMPORT ROCH TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue : {Product.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    run()
