"""
Import des Congélateurs Horizontaux Sharp pour Onizuka Shop
- Sharp 450 Litres Réf 580 : 435 000 FCFA
- Sharp 520 Litres Réf 660 : 489 000 FCFA
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

SHARP_PRODUCTS = [
    {
        'sku': 'ONZ-SHP-CH-450L',
        'name': 'Congélateur Coffre Horizontal Sharp 450 Litres - Super Fast Freezing Réf 580',
        'litres': 450,
        'model': 'Réf 580 / Super Fast Freezing',
        'price': 435000,
        'description': (
            "Congélateur coffre horizontal haut de gamme Sharp 450 litres (Réf 580), conçu avec l'ingénierie japonaise de précision "
            "« Trusted Japanese Brand ». Équipé de la technologie puissante « Sharp Super Fast Freezing » assurant une surgélation "
            "rapide à cœur et une préservation nutritionnelle irréprochable de vos aliments. Intègre un système exclusif de vitres "
            "coulissantes intérieures transparentes étanches empêchant le froid de s'échapper lors de l'ouverture du grand couvercle principal. "
            "Doté d'un éclairage intérieur automatique, d'un panier métallique suspendu amovible, d'une serrure à clé et d'un panneau de "
            "commande électronique avec témoins lumineux de fonctionnement et alarme. Compresseur tropicalisé ultra-robuste adapté aux "
            "conditions climatiques extrêmes de Bamako et aux fluctuations du réseau EDM. Vendu avec garantie officielle Onizuka Shop au Grand Marché (Dibidani)."
        ),
        'specs': {
            'Capacité nette': '450 Litres',
            'Référence modèle': 'Réf 580 / Super Fast Freezing',
            'Marque': 'Sharp (Trusted Japanese Brand)',
            'Technologie de froid': 'Super Fast Freezing (Surgélation ultra-rapide)',
            'Système thermique': 'Vitres coulissantes intérieures transparentes anti-déperdition',
            'Porte principale': '1 très large battant avec joint antibactérien démontable',
            'Sécurité': 'Serrure à clé intégrée',
            'Éclairage': 'Éclairage intérieur LED automatique',
            'Rangement': 'Panier métallique suspendu pour accès rapide',
            'Contrôle': 'Thermostat réglable frontal avec témoins Power, Run et Alerte',
            'Cuve intérieure': 'Aluminium gaufré martelé haute conduction et anti-rouille',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd spécial Bamako)',
            'Couleur': 'Gris Silver métallisé haute durabilité',
            'Vidange': 'Bouchon de dégivrage frontal pratique',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795792379006_4cebfb3a.jpg', 'dest': 'sharp_coffre_450l_ref580.webp', 'is_primary': True},
        ]
    },
    {
        'sku': 'ONZ-SHP-CH-520L',
        'name': 'Congélateur Coffre Horizontal Sharp 520 Litres PRO - 2 Battants Réf 660',
        'litres': 520,
        'model': 'Réf 660 / Super Fast Freezing 2 Battants',
        'price': 489000,
        'description': (
            "Le fleuron de la réfrigération horizontale japonaise : congélateur coffre Sharp 520 litres (modèle grand format Réf 660) "
            "avec double ouverture à deux battants indépendants. Conçu pour les exigences des commerces, supermarchés, boucheries, restaurants "
            "et résidences de grand standing à Bamako. Doté de la technologie d'avant-garde « Sharp Super Fast Freezing » capable de geler de gros "
            "volumes en un temps record. Équipé d'un équipement intérieur exceptionnel comprenant 4 paniers métalliques suspendus amovibles "
            "pour un classement parfait de vos vivres, de serrures de sécurité individuelles pour chaque battant et d'un double éclairage LED. "
            "Compresseur Inverter tropicalisé lourd offrant une endurance remarquable face aux fortes chaleurs et aux coupures de courant. "
            "Produit officiel garanti disponible chez Onizuka Shop à Dibidani."
        ),
        'specs': {
            'Capacité nette': '520 Litres',
            'Référence constructeur': 'Réf 660 / Super Fast Freezing',
            'Marque': 'Sharp (Trusted Japanese Brand)',
            'Type': 'Congélateur coffre professionnel 2 battants grand volume',
            'Portes / Battants': '2 grands battants indépendants avec serrures individuelles',
            'Équipement de rangement': '4 paniers métalliques suspendus amovibles',
            'Éclairage': 'Double éclairage intérieur LED automatique',
            'Sécurité': 'Double serrure à clé indépendante',
            'Cuve intérieure': 'Aluminium martelé gaufré anti-corrosion haute résistance',
            'Contrôle': 'Thermostat électronique frontal avec témoins LED de statut',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd spécial Bamako)',
            'Couleur': 'Gris métallisé premium anti-traces',
            'Vidange': 'Bouchon de vidange frontal pour dégivrage rapide',
        },
        'images': [
            {'src': USER_UPLOADED / 'media_1795792471406_b883b794.jpg', 'dest': 'sharp_coffre_520l_ref660_ferme.webp', 'is_primary': True},
            {'src': USER_UPLOADED / 'media_1795792424848_44e3111d.jpg', 'dest': 'sharp_coffre_520l_ref660_ouvert.webp', 'is_primary': False},
        ]
    }
]

def run():
    print("=== DÉBUT IMPORT DES CONGÉLATEURS COFFRES SHARP ===")
    
    brand = Brand.objects.get(slug='sharp')
    cat = Category.objects.get(slug='congelateurs-horizontaux')
    
    for item in SHARP_PRODUCTS:
        sku = item['sku']
        name = item['name']
        price = item['price']
        desc = item['description']
        specs = item['specs']
        
        print(f"\nTraitement {sku} - {name} ({price:,} FCFA)...")
        
        slug = slugify(f"congelateur-horizontal-sharp-{item['litres']}l-{slugify(item['model'])}")
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
                'is_featured': True,
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
                    alt_text=f"{product.name} - Vue réelle showroom Dibidani",
                    order=idx,
                    is_primary=img_info['is_primary']
                )
            else:
                print(f" [ATTENTION] Fichier introuvable: {src}")
                
        print(f" -> Images associées pour {sku}")
        
    print("\n=== IMPORT SHARP TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue : {Product.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    run()
