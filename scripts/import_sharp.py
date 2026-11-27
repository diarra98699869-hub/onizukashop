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

SRC_IMG = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729324020_5e5b1554.jpg"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Marque Sharp et Catégorie Climatiseurs
brand_sharp, _ = Brand.objects.get_or_create(
    slug="sharp",
    defaults={"name": "Sharp", "is_active": True, "description": "Sharp Japon - Leader des systèmes de climatisation robustes, fiables et endurants."}
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

# Copie de l'image
sharp_img_name = "sharp_split_standard_tropicalise.jpg"
sharp_img_path = os.path.join(MEDIA_PRODUCTS_DIR, sharp_img_name)
if os.path.exists(SRC_IMG):
    shutil.copy2(SRC_IMG, sharp_img_path)
    print(f"Image Sharp copiée vers {sharp_img_path}")
else:
    print(f"Attention: Image Sharp non trouvée à {SRC_IMG}")

SHARP_PRODUCTS = [
    {
        "name": "Climatiseur Split Sharp 1 CV (9000 BTU) Simple Tropicalisé",
        "power": "1.0 CV (9000 BTU)",
        "price": Decimal("155000"),
        "cost_price": Decimal("125000"),
        "stock": 10,
        "short_description": "Climatiseur split Sharp 1 CV standard simple, compresseur tropicalisé ultra robuste, froid rapide et tuyauterie cuivre.",
        "description": "Le Climatiseur Split Sharp 1 CV Simple (9000 BTU) est la référence japonaise de robustesse à Bamako. Conçu avec un compresseur standard tropicalisé à haute tolérance aux variations électriques et fortes chaleurs sahéliennes, il offre un souffle d'air puissant et un refroidissement direct et efficace. Façade élégante blanc pur avec liseré azur, filtre antibactérien amovible lavable, télécommande intuitive et kit de raccordement complet en cuivre inclus.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Standard Series",
            "Type": "Climatiseur Split Simple (Conventionnel)",
            "Puissance": "1.0 CV (9000 BTU)",
            "Climat": "Tropicalisé T3 haute endurance",
            "Accessoires": "Couronne de tuyauterie cuivre isolée + Télécommande",
            "Surface conseillée": "12 à 18 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Sharp 1.5 CV (12000 BTU) Simple Tropicalisé",
        "power": "1.5 CV (12000 BTU)",
        "price": Decimal("195000"),
        "cost_price": Decimal("155000"),
        "stock": 12,
        "short_description": "Climatiseur split Sharp 1.5 CV simple standard, le classique incontournable pour salons et chambres à Bamako.",
        "description": "Le Climatiseur Split Sharp 1.5 CV Simple (12000 BTU) est le modèle préféré pour les foyers et bureaux à Bamako. Alliant simplicité d'utilisation, compresseur robuste tropicalisé et maintenance facile, il garantit un abaissement rapide de la température dans des pièces de 18 à 28 m². Livré complet avec unité intérieure, groupe extérieur et tuyaux cuivre.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Standard Series 12K",
            "Type": "Climatiseur Split Simple",
            "Puissance": "1.5 CV (12000 BTU)",
            "Climat": "Tropicalisé T3",
            "Surface conseillée": "18 à 28 m²",
            "Fonctions": "Refroidissement rapide Turbo, Minuterie, Mode Nuit",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Sharp 2 CV (18000 BTU) Simple Tropicalisé",
        "power": "2.0 CV (18000 BTU)",
        "price": Decimal("265000"),
        "cost_price": Decimal("215000"),
        "stock": 8,
        "short_description": "Climatiseur split Sharp 2 CV simple tropicalisé grand débit d'air, idéal pour grands salons et boutiques.",
        "description": "Le Climatiseur Split Sharp 2 CV Simple (18000 BTU) procure un débit volumétrique d'air frais très puissant pour rafraîchir des espaces de 25 à 38 m². Son compresseur puissant résiste aux environnements poussiéreux et chauds. Volets motorisés pour une distribution uniforme de la fraîcheur.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Standard Series 18K",
            "Type": "Climatiseur Split Simple Grand Débit",
            "Puissance": "2.0 CV (18000 BTU)",
            "Surface conseillée": "25 à 38 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Sharp 2.5 CV (24000 BTU) Simple Tropicalisé",
        "power": "2.5 CV (24000 BTU)",
        "price": Decimal("330000"),
        "cost_price": Decimal("265000"),
        "stock": 6,
        "short_description": "Climatiseur split Sharp 2.5 CV simple très haute capacité pour grands salons, salles de conférence et magasins.",
        "description": "Climatiseur Split Sharp 2.5 CV Simple (24000 BTU) taillé pour les grands volumes (jusqu'à 50 m²). Puissance frigorifique maximale pour neutraliser instantanément la canicule extérieure. Matériaux haute qualité, compresseur haute pression tropicalisé, tuyauterie cuivre 100% résistante.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Standard Series 24K",
            "Type": "Climatiseur Split Simple Haute Puissance",
            "Puissance": "2.5 CV (24000 BTU)",
            "Surface conseillée": "35 à 50 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    }
]

print("Insertion des 4 modèles Sharp Simple...")

for idx, pdata in enumerate(SHARP_PRODUCTS, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-SHP-{idx:04d}"
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": cat_clim,
            "brand": brand_sharp,
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
    rel_path = f"products/{sharp_img_name}"
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
    print(f"[{idx}/4] OK: {product.name} | Prix Vente: {product.price:,} F | Prix Achat: {product.cost_price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")

print("\nPack Sharp Simple importé avec succès !")
