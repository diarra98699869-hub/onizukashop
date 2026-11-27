"""
Import du Congélateur Horizontal Telimani 212 Litres pour Onizuka Shop
Prix : 220 000 FCFA
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

def run():
    print("=== DÉBUT IMPORT DU CONGÉLATEUR TELIMANI 212L ===")
    
    brand, _ = Brand.objects.get_or_create(
        slug='telimani',
        defaults={
            'name': 'Telimani',
            'description': 'Marque réputée pour ses congélateurs coffres commerciaux et domestiques à haute rétention thermique.',
            'is_active': True,
        }
    )
    cat = Category.objects.get(slug='congelateurs-horizontaux')
    
    sku = 'ONZ-TEL-CH-212L'
    name = 'Congélateur Coffre Horizontal Telimani 212 Litres - Vitres Coulissantes Intérieures'
    price = 220000
    
    desc = (
        "Congélateur coffre horizontal Telimani (gamme Telimani Star) d'une capacité de 212 litres, "
        "spécialement pensé pour les commerces de quartier, les boutiques de glace, les épiceries et les foyers à Bamako. "
        "Intègre une double isolation remarquable : un grand couvercle supérieur doublé de vitres coulissantes transparentes "
        "avec poignées intégrées. Ce dispositif permet de servir rapidement ses clients ou de vérifier ses stocks sans laisser "
        "s'échapper le froid. Moteur tropicalisé conçu pour assurer une congélation constante à -18°C même lors des fortes chaleurs "
        "et coupures d'électricité. Livré avec un panier métallique suspendu amovible, un thermostat précis en façade avec voyants "
        "et un orifice de vidange avant. Disponible au showroom Onizuka Shop au Grand Marché de Bamako (Dibidani)."
    )
    
    specs = {
        'Capacité nette': '212 Litres',
        'Marque': 'Telimani (Telimani Star)',
        'Type': 'Congélateur coffre horizontal avec vitres thermiques',
        'Système double isolation': 'Vitres coulissantes intérieures transparentes avec poignées',
        'Porte principale': '1 large battant étanche avec joint démontable',
        'Sécurité': 'Serrure intégrée avec clé',
        'Rangement': 'Panier métallique suspendu amovible inclus',
        'Cuve intérieure': 'Aluminium gaufré martelé haute conduction et anti-corrosion',
        'Alimentation': '220V - 240V / 50Hz',
        'Classe climatique': 'T (Tropicalisé spécial Bamako / Afrique de l\'Ouest)',
        'Couleur': 'Gris Silver métallisé anti-traces',
        'Thermostat': 'Réglable multi-niveaux en façade avec témoins LED',
        'Vidange': 'Bouchon de dégivrage frontal pour un nettoyage aisé',
    }
    
    product, created = Product.objects.update_or_create(
        sku=sku,
        defaults={
            'name': name,
            'slug': slugify('congelateur-horizontal-telimani-212-litres'),
            'brand': brand,
            'category': cat,
            'price': price,
            'description': desc,
            'specifications': specs,
            'stock': 10,
            'track_stock': True,
            'status': Product.Status.ACTIVE,
            'is_active': True,
            'is_featured': True,
        }
    )
    print(f" -> Produit {'Créé' if created else 'Mis à jour'} (ID={product.id})")
    
    ProductImage.objects.filter(product=product).delete()
    
    img_closed = USER_UPLOADED / 'media_1795792552205_d94acf2a.jpg'
    img_open = USER_UPLOADED / 'media_1795792557606_bf955ddc.jpg'
    
    dest_closed = DEST_DIR / 'telimani_coffre_212l_ferme.webp'
    dest_open = DEST_DIR / 'telimani_coffre_212l_ouvert.webp'
    
    if img_closed.exists():
        convert_to_webp(img_closed, dest_closed)
        ProductImage.objects.create(
            product=product,
            image='products/congelateurs_coffres/telimani_coffre_212l_ferme.webp',
            alt_text=f"{product.name} - Vue fermée showroom Dibidani",
            order=0,
            is_primary=True,
        )
        
    if img_open.exists():
        convert_to_webp(img_open, dest_open)
        ProductImage.objects.create(
            product=product,
            image='products/congelateurs_coffres/telimani_coffre_212l_ouvert.webp',
            alt_text=f"{product.name} - Vue intérieure vitres coulissantes et panier",
            order=1,
            is_primary=False,
        )
        
    print(f"=== IMPORT TELIMANI TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue : {Product.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    run()
