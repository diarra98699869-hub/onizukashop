import os
import sys
import shutil
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onizouka.settings")
import django
django.setup()

from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

SRC_DIR = r"C:\Users\a\Downloads\2pack clim"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# Récupérer Marque Samsung et Catégorie Climatiseurs
brand_samsung, _ = Brand.objects.get_or_create(
    name="Samsung",
    defaults={"slug": "samsung", "is_active": True}
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

SAMSUNG_PRODUCTS = [
    {
        "name": "Climatiseur Split Samsung Digital Inverter 9000 BTU (1 CV) Gaz R32",
        "category": cat_clim,
        "brand": brand_samsung,
        "cost_price": 195000,
        "price": 242000,
        "sale_price": None,
        "stock": 10,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Climatiseur split Samsung Digital Inverter 1 CV (9000 BTU), technologie Inverter Boost ultra-économe, gaz R32 écologique, Triple Protector Plus.",
        "description": "Le Climatiseur Split Mural Samsung Digital Inverter 9000 BTU (1 CV) est la référence absolue en matière de confort thermique et d'efficacité énergétique pour les résidences et bureaux de standing à Bamako. Grâce à son compresseur exclusif Samsung Digital Inverter Boost, il refroidit la pièce 43% plus rapidement tout en réduisant la consommation électrique jusqu'à 73% par rapport aux modèles conventionnels. Équipé du nouveau gaz écologique R32, d'un filtre HD lavable haute densité anti-poussière et de la technologie Triple Protector Plus qui protège l'appareil contre les chutes et surtensions soudaines du réseau électrique sans stabilisateur externe. Livré complet avec unité intérieure design blanche, compresseur extérieur silencieux et télécommande avec écran rétroéclairé.",
        "specifications": {
            "Marque": "Samsung",
            "Modèle": "Digital Inverter Split Series",
            "Capacité": "9000 BTU/h (1.0 Cheval)",
            "Technologie compresseur": "Digital Inverter Boost 8 pôles",
            "Économie d'énergie": "Jusqu'à -73% de consommation",
            "Fluide frigorigène": "Gaz R32 écologique haute performance",
            "Protection électrique": "Triple Protector Plus (anti-surtension EDM intégrée)",
            "Échangeur thermique": "DuraFin+ avec traitement anti-corrosion",
            "Filtration": "Filtre HD lavable antibactérien et anti-poussière",
            "Surface recommandée": "12 à 18 m² (chambre, bureau)",
            "Modes": "Fast Cooling, Good Sleep, Déshumidificateur, Auto-Restart",
            "Garantie": "1 an officiel Onizuka Shop"
        },
        "images": [
            ("WhatsApp Image 2026-11-26 at 20.22.01.jpeg", "samsung_digital_inverter_9000btu_1.jpeg"),
            ("WhatsApp Image 2026-11-26 at 20.22.08.jpeg", "samsung_digital_inverter_9000btu_2.jpeg"),
            ("WhatsApp Image 2026-11-26 at 20.22.03.jpeg", "samsung_digital_inverter_9000btu_3.jpeg"),
        ]
    },
    {
        "name": "Climatiseur Split Samsung Digital Inverter 12000 BTU (1.5 CV) Gaz R32",
        "category": cat_clim,
        "brand": brand_samsung,
        "cost_price": 225000,
        "price": 282000,
        "sale_price": None,
        "stock": 12,
        "is_eco_solar": False,
        "is_featured": True,
        "short_description": "Climatiseur split Samsung Digital Inverter 1.5 CV (12000 BTU), refroidissement rapide, 100% silencieux, gaz écologique R32.",
        "description": "Le Climatiseur Split Mural Samsung Digital Inverter 12000 BTU (1.5 CV) offre la puissance idéale pour rafraîchir un salon spacieux ou une suite parentale à Bamako. Doté du moteur Samsung Digital Inverter à régulation millimétrée, il maintient la température désirée sans à-coups ni surconsommation. Sa conception aérodynamique à large entrée d'air et pales optimisées propulse l'air frais jusqu'à 15 mètres. Doté du fluide R32 nouvelle génération, du radiateur résistant DuraFin+ et du système de sécurité Triple Protector Plus conçu pour supporter les climats extrêmes et variations de courant.",
        "specifications": {
            "Marque": "Samsung",
            "Modèle": "Digital Inverter Split Series",
            "Capacité": "12000 BTU/h (1.5 Chevaux)",
            "Technologie compresseur": "Digital Inverter Boost haute précision",
            "Gaz frigorigène": "R32 éco-responsable",
            "Protection électrique": "Triple Protector Plus intégré",
            "Protection anticorrosion": "Ailerons DuraFin+ traités",
            "Surface recommandée": "18 à 28 m² (salons, grandes chambres)",
            "Niveau sonore": "Ultra silencieux (Mode Nuit Good Sleep)",
            "Garantie": "1 an officiel Onizuka Shop"
        },
        "images": [
            ("WhatsApp Image 2026-11-26 at 20.22.01.jpeg", "samsung_digital_inverter_12000btu_1.jpeg"),
            ("WhatsApp Image 2026-11-26 at 20.22.08.jpeg", "samsung_digital_inverter_12000btu_2.jpeg"),
            ("WhatsApp Image 2026-11-26 at 20.22.03.jpeg", "samsung_digital_inverter_12000btu_3.jpeg"),
        ]
    }
]

print("Insertion des climatiseurs Samsung Digital Inverter...")

for idx, pdata in enumerate(SAMSUNG_PRODUCTS, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-SAM-{idx:04d}"
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": pdata["category"],
            "brand": pdata["brand"],
            "cost_price": Decimal(str(pdata["cost_price"])),
            "price": Decimal(str(pdata["price"])),
            "sale_price": Decimal(str(pdata["sale_price"])) if pdata["sale_price"] else None,
            "stock": pdata["stock"],
            "min_stock": 2,
            "track_stock": True,
            "is_eco_solar": pdata["is_eco_solar"],
            "is_featured": pdata["is_featured"],
            "is_new": True,
            "is_active": True,
            "status": Product.Status.ACTIVE,
            "short_description": pdata["short_description"],
            "description": pdata["description"],
            "specifications": pdata["specifications"],
            "meta_title": f"{pdata['name']} - Prix Bamako | Onizuka Shop",
            "meta_description": pdata["short_description"][:160]
        }
    )
    
    if not created:
        product.price = Decimal(str(pdata["price"]))
        product.cost_price = Decimal(str(pdata["cost_price"]))
        product.stock = pdata["stock"]
        product.save()

    # Copie des images réelles
    for order_idx, (src_file, dst_file) in enumerate(pdata["images"]):
        src_path = os.path.join(SRC_DIR, src_file)
        if os.path.exists(src_path):
            dst_path = os.path.join(MEDIA_PRODUCTS_DIR, dst_file)
            shutil.copy2(src_path, dst_path)
            
            rel_path = f"products/{dst_file}"
            pimg, img_created = ProductImage.objects.get_or_create(
                product=product,
                image=rel_path,
                defaults={
                    "is_primary": (order_idx == 0),
                    "order": order_idx,
                    "alt_text": f"{product.name} Onizuka Shop Bamako"
                }
            )
            if not pimg.is_primary and order_idx == 0:
                pimg.is_primary = True
                pimg.save()

    margin = product.margin
    margin_pct = product.margin_percentage
    print(f"[{idx}] OK: {product.name} | Prix Vente: {product.price:,} F | Prix Achat: {product.cost_price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")

print("\nInsertion réussie !")
