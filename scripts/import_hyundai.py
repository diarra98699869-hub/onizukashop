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

SRC_IMG = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729489234_a9aa9c6a.jpg"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Marque Hyundai et Catégorie Climatiseurs
brand_hyundai, _ = Brand.objects.get_or_create(
    slug="hyundai",
    defaults={
        "name": "Hyundai",
        "is_active": True,
        "description": "Hyundai Electronics - Climatiseurs Inverter robustes, silencieux et ultra-économes en énergie."
    }
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

# Copie de l'image
hyundai_img_name = "hyundai_split_inverter_r410a_eco.jpg"
hyundai_img_path = os.path.join(MEDIA_PRODUCTS_DIR, hyundai_img_name)
if os.path.exists(SRC_IMG):
    shutil.copy2(SRC_IMG, hyundai_img_path)
    print(f"Image Hyundai copiée vers {hyundai_img_path}")
else:
    print(f"Attention: Image Hyundai non trouvée à {SRC_IMG}")

HYUNDAI_PRODUCTS = [
    {
        "name": "Climatiseur Split Hyundai Inverter 1 CV (9000 BTU) R410A ECO",
        "power": "1.0 CV (9000 BTU)",
        "price": Decimal("190000"),
        "cost_price": Decimal("150000"),
        "stock": 10,
        "short_description": "Climatiseur split Hyundai 1 CV Inverter, Fast Cooling, Low Noise ultra silencieux, Energy Saving jusqu'à -70% et gaz R410A ECO.",
        "description": "Le Climatiseur Split Mural Hyundai Inverter 1 CV (9000 BTU) combine l'excellence technologique coréenne et une résistance thermique extrême adaptée au climat de Bamako. Son compresseur Hyundai Inverter ajuste sa fréquence en continu pour une économie d'énergie radicale (Energy Saving). Équipé du mode Turbo pour un refroidissement rapide (Fast Cooling), d'un fonctionnement ultra silencieux (Low Noise) et du fluide frigorigène écologique R410A ECO. Livré complet avec unité intérieure design blanche, compresseur extérieur anticorrosion et télécommande infrarouge.",
        "specifications": {
            "Marque": "Hyundai",
            "Modèle": "Hyundai Inverter Series ECO",
            "Capacité": "1.0 CV (9000 BTU)",
            "Technologie compresseur": "Inverter DC Haute Efficacité",
            "Économie d'énergie": "Energy Saving certifié",
            "Niveau sonore": "Low Noise (ultra silencieux)",
            "Modes": "Fast Cooling, Turbo Mode, Eco Mode, Sleep Mode",
            "Gaz réfrigérant": "R410A ECO respectueux de l'environnement",
            "Surface conseillée": "12 à 18 m² (chambres, bureaux)",
            "Garantie": "1 an officiel Onizuka Shop (compresseur 5 ans)"
        }
    },
    {
        "name": "Climatiseur Split Hyundai Inverter 1.5 CV (12000 BTU) R410A ECO",
        "power": "1.5 CV (12000 BTU)",
        "price": Decimal("210000"),
        "cost_price": Decimal("165000"),
        "stock": 12,
        "short_description": "Climatiseur split Hyundai 1.5 CV Inverter, grand confort thermique, économie d'énergie et silence absolu pour salons et chambres.",
        "description": "Le Climatiseur Split Mural Hyundai Inverter 1.5 CV (12000 BTU) est le choix parfait pour rafraîchir un salon ou une grande chambre parentale à Bamako (18 à 28 m²). Grâce à son système Inverter intelligent, il maintient la pièce à une température idéale sans variation brutale ni surchauffe du réseau électrique. Doté des technologies Fast Cooling, Turbo Mode et du gaz écologique R410A ECO.",
        "specifications": {
            "Marque": "Hyundai",
            "Modèle": "Hyundai Inverter Series ECO 12K",
            "Capacité": "1.5 CV (12000 BTU)",
            "Technologie": "Inverter Basse Consommation",
            "Gaz réfrigérant": "R410A ECO",
            "Surface conseillée": "18 à 28 m²",
            "Fonctions": "Fast Cooling, Low Noise, Energy Saving, Turbo Mode",
            "Garantie": "1 an officiel Onizuka Shop (compresseur 5 ans)"
        }
    },
    {
        "name": "Climatiseur Split Hyundai Inverter 2 CV (18000 BTU) R410A ECO",
        "power": "2.0 CV (18000 BTU)",
        "price": Decimal("270000"),
        "cost_price": Decimal("215000"),
        "stock": 8,
        "short_description": "Climatiseur split Hyundai 2 CV Inverter haute puissance, grand volume de fraîcheur pour salons spacieux et bureaux professionnels.",
        "description": "Le Climatiseur Split Mural Hyundai Inverter 2 CV (18000 BTU) délivre un flux d'air puissant et homogène capable de couvrir des surfaces de 25 à 38 m². Son compresseur Inverter robuste est tropicalisé pour résister aux canicules les plus intenses tout en réduisant considérablement la facture d'électricité. Fiable, silencieux et garanti.",
        "specifications": {
            "Marque": "Hyundai",
            "Modèle": "Hyundai Inverter Series ECO 18K",
            "Capacité": "2.0 CV (18000 BTU)",
            "Technologie": "Inverter Haute Capacité",
            "Surface conseillée": "25 à 38 m²",
            "Gaz": "R410A ECO",
            "Garantie": "1 an officiel Onizuka Shop (compresseur 5 ans)"
        }
    }
]

print("Insertion des 3 modèles Hyundai Inverter...")

for idx, pdata in enumerate(HYUNDAI_PRODUCTS, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-HYU-{idx:04d}"
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": cat_clim,
            "brand": brand_hyundai,
            "cost_price": pdata["cost_price"],
            "price": pdata["price"],
            "sale_price": None,
            "stock": pdata["stock"],
            "min_stock": 2,
            "track_stock": True,
            "is_eco_solar": False,
            "is_featured": True,
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
        product.price = pdata["price"]
        product.cost_price = pdata["cost_price"]
        product.stock = pdata["stock"]
        product.save()

    # Rattacher l'image
    rel_path = f"products/{hyundai_img_name}"
    pimg, img_created = ProductImage.objects.get_or_create(
        product=product,
        image=rel_path,
        defaults={
            "is_primary": True,
            "order": 0,
            "alt_text": f"{product.name} Onizuka Shop Grand Marché Bamako Dibidani"
        }
    )
    if not pimg.is_primary:
        pimg.is_primary = True
        pimg.save()

    margin = product.margin
    margin_pct = product.margin_percentage
    print(f"[{idx}/3] OK: {product.name} | Prix Vente: {product.price:,} F | Prix Achat: {product.cost_price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")

print("\nPack Hyundai Inverter importé avec succès !")
