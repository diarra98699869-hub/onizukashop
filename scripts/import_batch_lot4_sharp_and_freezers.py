"""
Script d'importation Lot 4 Onizuka Shop :
- Gamme Réfrigérateurs Combinés Sharp (Japon Technology, Inox Titane, Defrost/No-Frost) :
    * Sharp SJ-BH180 (180 Litres / 138L net) — 220 000 FCFA
    * Sharp SJ-BH270 (270 Litres) — 285 000 FCFA
    * Sharp SJ-BH320 (320 Litres / 272L net) — 325 000 FCFA
    * Sharp SJ-BH400 (400 Litres / 332L net) — 365 000 FCFA

- Gamme Congélateurs Bahuts Vitrés Coulissants NS (Supermarché, Glaces & Boissons) :
    * NS-250A (250 Litres) — 220 000 FCFA
    * NS-380A (380 Litres) — 290 000 FCFA
    * NS-460A (460 Litres) — 350 000 FCFA
    * NS-580A (580 Litres) — 410 000 FCFA
    * NS-620A (620 Litres) — 485 000 FCFA
"""

import os
import sys
import shutil
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

import django
django.setup()

from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

MEDIA_PRODUCTS = BASE_DIR / 'media' / 'products'
MEDIA_PRODUCTS.mkdir(parents=True, exist_ok=True)

USER_UPLOADED_DIR = Path(r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded")

def copy_and_convert_image(src_name, dest_filename):
    dest_path = MEDIA_PRODUCTS / dest_filename
    if dest_path.exists():
        return f"products/{dest_filename}"
    
    src_path = USER_UPLOADED_DIR / src_name
    if src_path.exists():
        try:
            with Image.open(src_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=90, optimize=True)
            return f"products/{dest_filename}"
        except Exception as e:
            print(f"Erreur conversion {src_name}: {e}")
            shutil.copy2(src_path, dest_path)
            return f"products/{dest_filename}"
    else:
        print(f"Image introuvable dans uploads ({src_path}) et media ({dest_path})")
        return None

def get_or_create_cat(name, parent_slug=None, icon=None):
    slug = slugify(name)
    parent = None
    if parent_slug:
        parent = Category.objects.filter(slug=parent_slug).first()
    
    cat, created = Category.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'parent': parent,
            'icon': icon or 'shopping-bag',
            'is_active': True,
        }
    )
    if not created and parent and cat.parent != parent:
        cat.parent = parent
        cat.save()
    return cat

def get_or_create_brand(name):
    slug = slugify(name)
    brand, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name})
    return brand

def create_product(data, image_sources=None):
    slug = slugify(data['name'])
    base_slug = slug
    idx = 1
    while Product.objects.filter(slug=slug).exclude(sku=data['sku']).exists():
        slug = f"{base_slug}-{idx}"
        idx += 1
    
    price = data['price']
    sale_price = None
    if data.get('old_price') and data['old_price'] > price:
        sale_price = price
        regular_price = data['old_price']
    else:
        regular_price = price
    
    product, created = Product.objects.update_or_create(
        sku=data['sku'],
        defaults={
            'name': data['name'],
            'slug': slug,
            'category': data['category'],
            'brand': data.get('brand'),
            'price': regular_price,
            'sale_price': sale_price,
            'stock': data.get('stock', 10),
            'short_description': data.get('short_description', ''),
            'description': data.get('description', ''),
            'specifications': {f"spec_{i}": f for i, f in enumerate(data.get('features', []))},
            'is_featured': data.get('is_featured', False),
            'is_new': True,
            'status': 'in_stock',
            'is_active': True,
        }
    )
    
    if image_sources:
        for i, src in enumerate(image_sources):
            dest_name = f"{data['sku'].lower()}_{i+1}.jpg"
            rel_path = copy_and_convert_image(src, dest_name)
            if rel_path:
                img_obj, img_created = ProductImage.objects.get_or_create(
                    product=product,
                    image=rel_path,
                    defaults={'is_primary': (i == 0), 'order': i, 'alt_text': product.name}
                )
                if i == 0 and not product.images.filter(is_primary=True).exists():
                    img_obj.is_primary = True
                    img_obj.save()

    status_str = "CRÉÉ" if created else "MIS À JOUR"
    displayed_price = sale_price if sale_price else regular_price
    print(f"[{status_str}] {product.name} ({displayed_price:,} FCFA) - SKU: {product.sku}")
    return product

def run_import():
    print("=== DÉBUT IMPORTATION DU LOT 4 (SHARP & CONGÉLATEURS VITRÉS NS) ===")
    
    # 1. Catégories & Marques
    cat_refrig = Category.objects.filter(slug='refrigerateurs-congelateurs').first() or get_or_create_cat("Réfrigérateurs & Congélateurs", icon="refrigerator")
    cat_vitrines = Category.objects.filter(slug='vitrines-refrigerees').first() or get_or_create_cat("Vitrines Réfrigérées", parent_slug=cat_refrig.slug, icon="store")
    
    b_sharp = get_or_create_brand("Sharp")
    b_ns = get_or_create_brand("NS")

    # --- 2. RÉFRIGÉRATEURS COMBINÉS SHARP ---
    # 2.1 Sharp SJ-BH180 (220 000 FCFA)
    create_product({
        "sku": "SHARP-SJ-BH180",
        "name": "Réfrigérateur Combiné Sharp 180 Litres SJ-BH180 Inox Titane (Technologie Japon)",
        "price": 220000,
        "old_price": 245000,
        "category": cat_refrig,
        "brand": b_sharp,
        "short_description": "Réfrigérateur combiné Sharp 180L (138L net), technologie Defrost Japonaise, classe énergétique A+, finition gris titane brossé.",
        "description": "La renommée technologique japonaise au service de la conservation de vos aliments à Bamako. Le réfrigérateur combiné Sharp SJ-BH180 offre un volume de 180 Litres idéal pour les foyers de taille moyenne, appartements ou bureaux. Il combine un compartiment réfrigérateur supérieur avec clayettes en verre sécurit et bac à légumes 'Keep Fresh Eat Healthy', ainsi qu'un congélateur bas à 3 tiroirs indépendants pour éviter les mélanges d'odeurs et congeler rapidement viandes et poissons.",
        "features": [
            "Marque : Sharp Corporation (Technologie Japonaise certifiée)",
            "Modèle : SJ-BH180 (Volume net 138L / Brut 180L)",
            "Configuration : Combiné 2 portes (Réfrigérateur haut + Congélateur bas 3 tiroirs)",
            "Finition : Acier brossé Inox Titane anti-traces de doigts",
            "Éclairage : Lumière intérieure LED économique et brillante",
            "Climatique : Catégorie T Tropicalisée ultra-résistante à la chaleur de Bamako",
            "Silencieux & Économe : Faible consommation électrique et compresseur stable",
            "Livraison et installation offertes à Bamako par Onizuka Shop"
        ],
        "is_featured": False,
    }, [
        "media_1795873510905_dcb4ffa7.jpg",
        "media_1795873485561_fa5283f2.jpg",
        "media_1795873495952_f6c4d82a.jpg"
    ])

    # 2.2 Sharp SJ-BH270 (285 000 FCFA)
    create_product({
        "sku": "SHARP-SJ-BH270",
        "name": "Réfrigérateur Combiné Sharp 270 Litres SJ-BH270 Inox Titane Tropicalisé",
        "price": 285000,
        "old_price": 315000,
        "category": cat_refrig,
        "brand": b_sharp,
        "short_description": "Réfrigérateur combiné Sharp grand format 270L, compresseur tropicalisé haute performance, congélateur 3 grands tiroirs.",
        "description": "Idéal pour une conservation saine et durable au quotidien. Le combiné Sharp SJ-BH270 270 Litres allie une grande capacité intérieure et un encombrement maîtrisé au sol. Clayettes réglables en verre trempé pour les grandes marmites, bac à fruits et légumes haute humidité, et congélateur inférieur puissant avec tiroirs transparents à glissière fluide. Design moderne en acier brossé titane.",
        "features": [
            "Marque : Sharp Corporation",
            "Modèle : SJ-BH270",
            "Volume total : 270 Litres",
            "Système de froid : Froid ventilé homogène Defrost Technology",
            "Aménagement : 3 clayettes verre trempé + grand bac fraîcheur + 3 tiroirs de congélation",
            "Poignées : Poignées intégrées profilées invisibles",
            "Performances : Compresseur renforcé pour fonctionnement continu par forte chaleur",
            "Garantie Onizuka Shop avec livraison à domicile à Bamako"
        ],
        "is_featured": True,
    }, [
        "media_1795873464072_8bbe9039.jpg",
        "media_1795873457983_1601a2ee.jpg",
        "media_1795873470798_05b1995b.jpg"
    ])

    # 2.3 Sharp SJ-BH320 (325 000 FCFA)
    create_product({
        "sku": "SHARP-SJ-BH320",
        "name": "Réfrigérateur Combiné Sharp 320 Litres SJ-BH320 Inox Titane (272L Net)",
        "price": 325000,
        "old_price": 360000,
        "category": cat_refrig,
        "brand": b_sharp,
        "short_description": "Combiné Sharp 320L grande capacité, clayettes modulables verre sécurit, congélateur 3 bacs ultra-profonds.",
        "description": "Le réfrigérateur combiné familial par excellence ! Avec ses 320 Litres de volume (272L net), le Sharp SJ-BH320 stocke facilement les courses hebdomadaires d'une famille complète. Sa technologie de froid maintient une température uniforme sur tous les étages pour préserver la fraîcheur des aliments jusqu'à 3 fois plus longtemps. Finition haut de gamme acier inoxydable gris titane.",
        "features": [
            "Marque : Sharp Corporation",
            "Modèle : SJ-BH320 (Capacité nette 272 Litres / Brut 320L)",
            "Double porte : Compartiment réfrigérateur haut + Congélateur bas",
            "Technologie : Froid ventilé antibactérien avec contrôle thermostatique précis",
            "Balconnets de porte : Larges emplacements pour bouteilles de 1.5L et 2L",
            "Finition : Inox Titane luxe résistant à la corrosion",
            "Service : Livraison et déballage soignés à Bamako inclus"
        ],
        "is_featured": True,
    }, [
        "media_1795873517974_3e031371.jpg",
        "media_1795873478306_aeff1d2a.jpg"
    ])

    # 2.4 Sharp SJ-BH400 (365 000 FCFA)
    create_product({
        "sku": "SHARP-SJ-BH400",
        "name": "Réfrigérateur Combiné Sharp 400 Litres SJ-BH400-HS2 Inox Titane (332L Net)",
        "price": 365000,
        "old_price": 400000,
        "category": cat_refrig,
        "brand": b_sharp,
        "short_description": "Le vaisseau amiral des combinés Sharp 400L, classe climatique T tropicalisée, froid No-Frost, 4 niveaux et bacs fraîcheur.",
        "description": "Le modèle le plus spacieux et performant de la gamme Sharp. Le combiné SJ-BH400-HS2 offre 400 Litres de volume brut (332L net certifié) avec 4 grandes clayettes en verre trempé ultra-résistantes, 2 bacs de conservation séparés (fruits, légumes, produits frais), et un congélateur inférieur XXL équipé de 3 grands tiroirs hermétiques. Sa classe climatique T garantit un fonctionnement impeccable même au-delà de 43°C à l'ombre à Bamako. Compresseur R600a écologique et ultra-économe.",
        "features": [
            "Marque : Sharp Corporation (Osaka, Japan)",
            "Modèle officiel : SJ-BH400-HS2 (332L Net / 400L Brut)",
            "Classe climatique : T (Tropicalisé spécial Afrique de l'Ouest / Mali)",
            "Puissance totale : 150W économique - Gaz réfrigérant R600a respectueux de l'environnement",
            "Agencement : 4 clayettes verre trempé + 2 bacs fraîcheur + 3 tiroirs congélation",
            "Éclairage : LED interne haute visibilité",
            "Poids : 58 kg robuste et stable",
            "Livraison, installation et garantie officielle par Onizuka Shop à Bamako"
        ],
        "is_featured": True,
    }, [
        "media_1795873503681_d786c3ed.jpg",
        "media_1795873247312_32856f4c.jpg",
        "media_1795873241041_98389e7f.jpg",
        "media_1795873234618_3e0a617a.jpg"
    ])

    # --- 3. CONGÉLATEURS VITRÉS HORIZONTAUX NS (PORTES VITRÉES COULISSANTES) ---
    # 3.1 NS-250A (220 000 FCFA)
    create_product({
        "sku": "NS-250A-VITRE",
        "name": "Congélateur Vitré Horizontal Coulissant NS 250 Litres NS-250A (Spécial Glaces & Boissons)",
        "price": 220000,
        "old_price": 250000,
        "category": cat_vitrines,
        "brand": b_ns,
        "short_description": "Congélateur bahut vitrine 250L à portes vitrées coulissantes bombées, idéal supérettes, boutiques et maquis.",
        "description": "Le congélateur bahut vitré professionnel compact par excellence pour commerces, alimentations générales, maquis et kiosques à Bamako. Équipé de portes vitrées coulissantes en verre trempé traité anti-condensation pour une visibilité totale de vos produits surgelés (glaces, poissons, poulets, jus et boissons fraîches). Économique, robuste et sur roulettes pour un déplacement sans effort.",
        "features": [
            "Marque : NS (Gamme Professionnelle)",
            "Modèle : NS-250A",
            "Capacité : 250 Litres",
            "Portes : Double porte vitrée coulissante en verre sécurit avec cadre profilé",
            "Panier : Panier suspendu métallique inclus pour séparation des produits",
            "Thermostat : Réglable en façade avec voyant lumineux de marche",
            "Mobilité : 4 roulettes multidirectionnelles robustes",
            "Livraison express sur votre point de vente à Bamako"
        ],
        "is_featured": False,
    }, ["media_1795873542069_b32c19b9.jpg"])

    # 3.2 NS-380A (290 000 FCFA)
    create_product({
        "sku": "NS-380A-VITRE",
        "name": "Congélateur Vitrine Horizontale Coulissante NS 380 Litres NS-380A Commercial",
        "price": 290000,
        "old_price": 325000,
        "category": cat_vitrines,
        "brand": b_ns,
        "short_description": "Congélateur vitrine 380L commercial, portes vitrées coulissantes panoramiques, éclairage et paniers inclus.",
        "description": "Optimisez vos ventes en libre-service grâce à cette vitrine congélateur horizontale NS-380A de 380 Litres. Ses grandes portes vitrées coulissantes permettent aux clients de voir instantanément le contenu sans déperdition de froid. Cuve intérieure en aluminium gaufré à haute conduction thermique et compresseur tropicalisé conçu pour un usage commercial intensif.",
        "features": [
            "Marque : NS Commercial Display Freezer",
            "Modèle : NS-380A",
            "Volume : 380 Litres format intermédiaire idéal",
            "Portes : Vitrage coulissant thermique à fermeture douce",
            "Équipement : Panier de rangement suspendu amovible",
            "Dégivrage : Orifice de vidange d'eau de dégivrage en façade",
            "Efficacité énergétique : Classe A optimisée pour minimiser la facture d'électricité",
            "Livraison et installation professionnelles à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795873542069_b32c19b9.jpg"])

    # 3.3 NS-460A (350 000 FCFA)
    create_product({
        "sku": "NS-460A-VITRE",
        "name": "Congélateur Vitrine Horizontale Coulissante NS 460 Litres NS-460A Grand Format",
        "price": 350000,
        "old_price": 390000,
        "category": cat_vitrines,
        "brand": b_ns,
        "short_description": "Congélateur bahut vitré 460L grande cuve, parfait supermarchés, poissonneries et glaciers à Bamako.",
        "description": "Une capacité généreuse de 460 Litres pour maximiser le stockage et la présentation de vos produits surgelés. Le NS-460A assure une congélation rapide et uniforme jusqu'à -18°C. Son isolation renforcée haute densité conserve le froid même en cas de coupure de courant prolongée. Cadre supérieur en aluminium satiné et portes coulissantes fluides avec poignées ergonomiques.",
        "features": [
            "Marque : NS Commercial",
            "Modèle : NS-460A",
            "Capacité : 460 Litres grande largeur",
            "Portes : Coulissantes en verre trempé renforcé haute transparence",
            "Conservation : Maintien du froid prolongé en cas de coupure d'électricité",
            "Cuve : Aluminium blanc facile à désinfecter et à nettoyer",
            "Roulettes : 4 roulettes renforcées haute charge pour faciliter le ménage",
            "Livraison sur site à Bamako par Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795873548025_3264bd9d.jpg"])

    # 3.4 NS-580A (410 000 FCFA)
    create_product({
        "sku": "NS-580A-VITRE",
        "name": "Congélateur Vitrine Horizontale Coulissante NS 580 Litres NS-580A Professionnel",
        "price": 410000,
        "old_price": 460000,
        "category": cat_vitrines,
        "brand": b_ns,
        "short_description": "Congélateur bahut vitrine 580L capacité XXL, compresseur surpuissant tropicalisé, paniers multiples.",
        "description": "Le choix incontournable pour les commerces à fort débit, grossistes de viande, poissonneries et grandes surfaces alimentaires. Avec son volume gigantesque de 580 Litres, le NS-580A permet d'exposer et de stocker d'importants volumes de marchandises en toute sécurité. Compresseur industriel tropicalisé conçu pour tourner sans faiblir sous les températures sahéliennes les plus extrêmes.",
        "features": [
            "Marque : NS Professional",
            "Modèle : NS-580A",
            "Capacité XXL : 580 Litres",
            "Portes : Verre trempé Low-E anti-buée et anti-rayures",
            "Froid : Froid statique puissant haute vitesse de congélation",
            "Châssis : Caisson en acier laqué blanc traité anticorrosion",
            "Isolation : Mousse polyuréthane injectée ultra-dense 75 mm",
            "Livraison et mise en place dans votre commerce à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795873563411_f2b36997.jpg"])

    # 3.5 NS-620A (485 000 FCFA)
    create_product({
        "sku": "NS-620A-VITRE",
        "name": "Congélateur Vitrine Horizontale Coulissante NS 620 Litres NS-620A Format Géant",
        "price": 485000,
        "old_price": 540000,
        "category": cat_vitrines,
        "brand": b_ns,
        "short_description": "Le plus grand congélateur vitrine 620L, double vitrage panoramique coulissant, capacité monumentale.",
        "description": "Le colosse de la gamme vitrine réfrigérée NS ! Ce congélateur bahut horizontal de 620 Litres offre une surface d'exposition et un volume de stockage inégalés. Il transforme votre magasin en véritable point de vente attractif pour les glaces, sachets de frites, volailles et poissons entiers. Double porte vitrée coulissante à glissement ultra-souple, double panier intérieur renforcé et compresseur tropicalisé haute efficacité énergétique.",
        "features": [
            "Marque : NS Professional Display",
            "Modèle : NS-620A Format Géant",
            "Capacité colossale : 620 Litres",
            "Vitrage : Verre sécurit trempé double épaisseur traité contre la chaleur",
            "Compresseur : Compresseur industriel tropicalisé haute fiabilité",
            "Paniers : Paniers de présentation inclus pour trier les références",
            "Sécurité : Serrure intégrée pour verrouiller l'accès aux marchandises hors heures d'ouverture",
            "Livraison directe avec équipe de manutention dédiée à Bamako par Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795873555540_0d682740.jpg"])

    print("\n🎉 === IMPORTATION DU LOT 4 TERMINÉE AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    run_import()
