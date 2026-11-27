"""
Import et Recadrage Haute Définition des Congélateurs Coffres :
- NAFA BD-398 (348L) : 235 000 FCFA
- NAFA BD-298 (248L) : 195 000 FCFA
- NAFA BD-198 (148L) : 173 000 FCFA
- Telimani 650L PRO (2 battants) : 520 000 FCFA
- LG 345L GCS415GQFG : 380 000 FCFA

Règle stricte : Recadrage chirurgical (crop) pour supprimer toutes les personnes,
passants, têtes en arrière-plan, chaussures au sol, motos et éléments encombrants.
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

def crop_and_convert_webp(src_path: Path, dest_path: Path, crop_box=None):
    """Rogner les personnes/encombrements et convertir en WebP haute fidélité."""
    with Image.open(src_path) as im:
        rgb_im = im.convert('RGB')
        if crop_box:
            rgb_im = rgb_im.crop(crop_box)
        rgb_im.save(dest_path, 'WEBP', quality=90, method=6)
    print(f" -> Image rognée & WebP: {dest_path.name} (Taille: {rgb_im.size[0]}x{rgb_im.size[1]}, {dest_path.stat().st_size // 1024} Ko)")

PRODUCTS = [
    # 1. NAFA 348L
    {
        'brand': 'NAFA',
        'brand_slug': 'nafa',
        'brand_desc': 'Marque d\'appareils électroménagers robustes et durables avec compresseur garanti 36 mois.',
        'sku': 'ONZ-NAFA-CH-348L',
        'name': 'Congélateur Coffre Horizontal NAFA BD-398 Couché 348 Litres',
        'litres': 348,
        'model': 'BD-398',
        'price': 235000,
        'description': (
            "Congélateur coffre horizontal NAFA couché d'une capacité de 348 litres (modèle officiel BD-398). "
            "Reconnu pour sa durabilité exceptionnelle et sa technologie de conservation longue durée avec compresseur "
            "tropicalisé garanti 36 mois. Dispose d'un grand battant étanche avec joint thermique renforcé, d'une cuve "
            "intérieure facile d'entretien, d'un panier métallique suspendu et d'une classe énergétique performante. "
            "Maintient le froid pendant de longues heures lors des délestages électriques à Bamako. Vendu neuf avec garantie "
            "officielle chez Onizuka Shop au Grand Marché (Dibidani)."
        ),
        'specs': {
            'Capacité nette': '348 Litres (Brut 398L)',
            'Modèle': 'BD-398 Couché',
            'Marque': 'NAFA (Le Choix Durable)',
            'Garantie compresseur': '36 Mois constructeur',
            'Type': 'Congélateur coffre horizontal grande capacité',
            'Porte / Battant': '1 large battant avec charnières équilibrées',
            'Rangement': 'Panier métallique suspendu inclus',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe énergétique': 'A+ Faible consommation électrique',
            'Classe climatique': 'T (Tropicalisé Sahel / Bamako)',
            'Couleur': 'Gris Silver métallisé',
            'Vidange': 'Bouchon de purge frontal pratique',
        },
        'images': [
            {
                'src': USER_UPLOADED / 'media_1795792579525_f7ef3895.jpg',
                'dest': 'nafa_coffre_348l_bd398.webp',
                'crop': (115, 205, 720, 930), # Supprime étagères et plafond
                'is_primary': True,
            }
        ]
    },
    # 2. NAFA 248L
    {
        'brand': 'NAFA',
        'brand_slug': 'nafa',
        'brand_desc': 'Marque d\'appareils électroménagers robustes et durables avec compresseur garanti 36 mois.',
        'sku': 'ONZ-NAFA-CH-248L',
        'name': 'Congélateur Coffre Horizontal NAFA BD-298 Couché 248 Litres',
        'litres': 248,
        'model': 'BD-298',
        'price': 195000,
        'description': (
            "Congélateur coffre horizontal NAFA 248 litres (modèle BD-298 couché), le compromis idéal entre encombrement maîtrisé "
            "et volume de stockage généreux. Équipé d'un compresseur tropicalisé haute performance garanti 3 ans (36 mois) par NAFA. "
            "Offre une descente rapide en température jusqu'à -18°C, une cuve intérieure étanche avec panier de tri, un thermostat réglable "
            "en façade et un joint antibactérien amovible. Faible consommation électrique adaptée aux compteurs EDM. "
            "Disponible immédiatement au showroom Dibidani avec livraison express partout à Bamako."
        ),
        'specs': {
            'Capacité nette': '248 Litres (Brut 298L)',
            'Modèle': 'BD-298 Couché',
            'Marque': 'NAFA (Le Choix Durable)',
            'Garantie compresseur': '36 Mois (3 ans)',
            'Type': 'Congélateur coffre horizontal couché',
            'Porte / Battant': '1 battant avec joint isolant épais',
            'Rangement': 'Panier métallique suspendu',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe énergétique': 'A+ Économique',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris métallisé premium',
            'Vidange': 'Évacuation frontale de dégivrage',
        },
        'images': [
            {
                'src': USER_UPLOADED / 'media_1795792643087_6c81ca15.jpg',
                'dest': 'nafa_coffre_248l_bd298.webp',
                'crop': (115, 205, 645, 955), # Supprime la personne dans la porte au fond et le rafraîchisseur
                'is_primary': True,
            }
        ]
    },
    # 3. NAFA 148L
    {
        'brand': 'NAFA',
        'brand_slug': 'nafa',
        'brand_desc': 'Marque d\'appareils électroménagers robustes et durables avec compresseur garanti 36 mois.',
        'sku': 'ONZ-NAFA-CH-148L',
        'name': 'Congélateur Coffre Horizontal NAFA BD-198 Couché 148 Litres Compact',
        'litres': 148,
        'model': 'BD-198',
        'price': 173000,
        'description': (
            "Congélateur coffre horizontal NAFA 148 litres (modèle BD-198 couché), compact, robuste et extrêmement économe en énergie. "
            "Parfait pour les petits commerces, boutiques, kiosques et foyers à Bamako. Bénéficie de la garantie compresseur 36 mois NAFA "
            "assurant une totale tranquillité d'esprit. Cuve intérieure traitée anti-corrosion, panier métallique suspendu, thermostat en façade "
            "et isolation thermique épaisse préservant vos produits congelés. Disponible chez Onizuka Shop au Grand Marché de Bamako."
        ),
        'specs': {
            'Capacité nette': '148 Litres (Brut 198L)',
            'Modèle': 'BD-198 Couché',
            'Marque': 'NAFA (Le Choix Durable)',
            'Garantie compresseur': '36 Mois constructeur',
            'Type': 'Congélateur coffre horizontal compact',
            'Porte / Battant': '1 battant supérieur équilibré',
            'Rangement': 'Panier métallique pour petits articles',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe énergétique': 'A+ Très basse consommation',
            'Classe climatique': 'T (Tropicalisé)',
            'Couleur': 'Gris Silver métallisé',
            'Vidange': 'Bouchon de purge en façade',
        },
        'images': [
            {
                'src': USER_UPLOADED / 'media_1795792748690_80c50492.jpg',
                'dest': 'nafa_coffre_148l_bd198.webp',
                'crop': (180, 55, 630, 920), # Supprime la personne debout à droite et les cartons à gauche
                'is_primary': True,
            }
        ]
    },
    # 4. Telimani 650L PRO
    {
        'brand': 'Telimani',
        'brand_slug': 'telimani',
        'brand_desc': 'Marque réputée pour ses congélateurs coffres commerciaux et domestiques à haute rétention thermique.',
        'sku': 'ONZ-TEL-CH-650L',
        'name': 'Congélateur Coffre Horizontal Telimani 650 Litres PRO - 2 Battants Géants',
        'litres': 650,
        'model': 'Telimani Star 650L PRO',
        'price': 520000,
        'description': (
            "Le géant de la gamme Telimani : congélateur coffre professionnel de 650 litres à deux battants indépendants. "
            "Conçu pour un usage commercial lourd (supérettes, grossistes, boucheries, poissonneries, boutiques de glaces et restaurants) à Bamako. "
            "Équipé d'une double baie de vitres coulissantes transparentes étanches permettant de conserver l'intégralité du froid lors de l'accès aux vivres. "
            "Compresseur tropicalisé ultra-puissant assurant une congélation profonde continue à -18°C même lors des périodes de canicule. "
            "Double éclairage LED intérieur, double serrure à clé, cuve en aluminium gaufré martelé et roulettes de déplacement renforcées. "
            "Garanti Onizuka Shop à Dibidani avec assistance technique dédiée."
        ),
        'specs': {
            'Capacité brute / nette': '650 Litres',
            'Marque': 'Telimani (Telimani Star)',
            'Type': 'Congélateur coffre professionnel 2 battants géants',
            'Portes / Battants': '2 très grands battants indépendants',
            'Isolation thermique': 'Vitres coulissantes intérieures transparentes étanches',
            'Sécurité': 'Double serrure à clé individuelle',
            'Éclairage': 'Double éclairage intérieur LED',
            'Rangement': 'Grands paniers métalliques suspendus',
            'Cuve intérieure': 'Aluminium gaufré martelé haute conductivité thermique',
            'Alimentation': '220V - 240V / 50Hz',
            'Classe climatique': 'T (Tropicalisé lourd spécial Mali)',
            'Couleur': 'Gris Silver métallisé haute durabilité',
            'Vidange': 'Bouchon de dégivrage frontal',
        },
        'images': [
            {
                'src': USER_UPLOADED / 'media_1795792835692_c05aff84.jpg',
                'dest': 'telimani_coffre_650l_ferme.webp',
                'crop': (80, 205, 745, 625), # Supprime chaussures au sol et plafond
                'is_primary': True,
            },
            {
                'src': USER_UPLOADED / 'media_1795792765776_86960912.jpg',
                'dest': 'telimani_coffre_650l_ouvert.webp',
                'crop': (35, 115, 715, 680), # Supprime têtes des 2 hommes au fond et chaussures
                'is_primary': False,
            }
        ]
    },
    # 5. LG 345L GCS415GQFG
    {
        'brand': 'LG',
        'brand_slug': 'lg',
        'brand_desc': 'Leader mondial de l\'électroménager premium et des technologies Inverter.',
        'sku': 'ONZ-LG-CH-345L',
        'name': 'Congélateur Coffre Horizontal LG 345 Litres - Inverter Modèle GCS415GQFG',
        'litres': 345,
        'model': 'GCS415GQFG',
        'price': 380000,
        'description': (
            "Congélateur coffre horizontal officiel LG 345 litres (modèle certifié GCS415GQFG) d'une fiabilité exceptionnelle. "
            "Doté du compresseur Smart Inverter LG de 190W alliant un silence de fonctionnement parfait et une très faible consommation électrique (1.5A). "
            "Capacité de congélation rapide de 17 kg/24h avec fluide écologique R600a et isolation thermique haute densité au Cyclopentane. "
            "Finition gris métallisé haute résistance contre la rouille, cuve spacieuse de 1275 x 740 x 825 mm avec paniers métalliques suspendus, "
            "éclairage intérieur et contrôle précis en façade. Conçu pour résister aux climats tropicaux et aux variations de tension électrique. "
            "Produit 100% authentique LG garanti avec facture officielle Onizuka Shop au Grand Marché de Bamako (Dibidani)."
        ),
        'specs': {
            'Capacité ISO stockage': '345 Litres',
            'Modèle constructeur': 'GCS415GQFG (AXGPW / 5N1F901)',
            'Marque': 'LG Electronics (Authentique certifié)',
            'Puissance moteur': '190W / 1.5A (Basse consommation)',
            'Gaz réfrigérant': 'R600a (98g) écologique',
            'Capacité de congélation': '17 kg / 24 heures',
            'Isolation thermique': 'Cyclopentane haute densité',
            'Dimensions (L x P x H)': '1275 x 740 x 825 mm',
            'Poids net': '55 kg',
            'Alimentation': '220V - 50Hz',
            'Classe climatique': 'ST (Semi-tropicalisé / Tropical)',
            'Couleur': 'Gris Silver métallisé anti-traces',
            'Rangement': 'Panier métallique suspendu pour tri rapide',
        },
        'images': [
            {
                'src': USER_UPLOADED / 'media_1795792886538_685675b9.jpg',
                'dest': 'lg_coffre_345l_ferme.webp',
                'crop': (30, 265, 576, 960), # Supprime rue, taxi et motos
                'is_primary': True,
            },
            {
                'src': USER_UPLOADED / 'media_1795792892342_1ae739a0.jpg',
                'dest': 'lg_coffre_345l_ouvert.webp',
                'crop': (15, 50, 576, 945), # Supprime personnes et rue
                'is_primary': False,
            },
            {
                'src': USER_UPLOADED / 'media_1795792900144_6e3c229f.jpg',
                'dest': 'lg_coffre_345l_plaque_technique.webp',
                'crop': (20, 180, 576, 520), # Recadrage net sur la plaque officielle LG
                'is_primary': False,
            }
        ]
    }
]

# Recadrage propre des anciens modèles qui avaient des passants
POLISH_EXISTING = [
    {
        'sku': 'ONZ-ROCH-CH-316L',
        'src': USER_UPLOADED / 'media_1795791994404_551ad0ac.jpg',
        'dest': 'roch_coffre_316l_ferme.webp',
        'crop': (40, 285, 555, 790), # Supprime voiture, moto et passants
    },
    {
        'sku': 'ONZ-ROCH-CH-550L',
        'src': USER_UPLOADED / 'media_1795791951332_fad64636.jpg',
        'dest': 'roch_coffre_550l_ferme.webp',
        'crop': (60, 20, 915, 525), # Supprime les jambes à gauche et le tricycle
    }
]

def run():
    print("=== DÉBUT IMPORT & RECADRAGE CHIRURGICAL ===")
    cat = Category.objects.get(slug='congelateurs-horizontaux')
    
    # 1. Nettoyage des images existantes pour Roch
    for pol in POLISH_EXISTING:
        dest_file = DEST_DIR / pol['dest']
        if pol['src'].exists():
            crop_and_convert_webp(pol['src'], dest_file, pol['crop'])
            
    # 2. Création et recadrage des 5 nouveaux produits
    for item in PRODUCTS:
        brand, _ = Brand.objects.get_or_create(
            slug=item['brand_slug'],
            defaults={
                'name': item['brand'],
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
        
        slug = slugify(f"congelateur-horizontal-{item['brand_slug']}-{item['litres']}l-{slugify(item['model'])}")
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
                'is_featured': True if item['litres'] in (345, 650) else False,
            }
        )
        print(f" -> Produit {'Créé' if created else 'Mis à jour'} (ID={product.id})")
        
        ProductImage.objects.filter(product=product).delete()
        for idx, img_info in enumerate(item['images']):
            src = img_info['src']
            dest_name = img_info['dest']
            dest_file = DEST_DIR / dest_name
            crop_box = img_info.get('crop')
            
            if src.exists():
                crop_and_convert_webp(src, dest_file, crop_box)
                rel_path = f"products/congelateurs_coffres/{dest_name}"
                ProductImage.objects.create(
                    product=product,
                    image=rel_path,
                    alt_text=f"{product.name} - Vue studio showroom Dibidani",
                    order=idx,
                    is_primary=img_info['is_primary']
                )
            else:
                print(f" [ATTENTION] Fichier introuvable: {src}")
                
        print(f" -> Images rognées et associées pour {sku}")
        
    print("\n=== IMPORT & RECADRAGE TERMINÉ AVEC SUCCÈS ===")
    print(f"Total produits actifs dans le catalogue : {Product.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    run()
