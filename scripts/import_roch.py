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

SRC_IMG = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729394846_41850a13.jpg"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Marque Roch et Catégorie Climatiseurs
brand_roch, _ = Brand.objects.get_or_create(
    slug="roch",
    defaults={
        "name": "Roch",
        "is_active": True,
        "description": "Roch - Électroménager et climatisation grand public accessible, robuste et parfaitement adapté au climat de Bamako."
    }
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

# Copie de l'image
roch_img_name = "roch_split_simple_tropicalise.jpg"
roch_img_path = os.path.join(MEDIA_PRODUCTS_DIR, roch_img_name)
if os.path.exists(SRC_IMG):
    shutil.copy2(SRC_IMG, roch_img_path)
    print(f"Image Roch copiée vers {roch_img_path}")
else:
    print(f"Attention: Image source Roch non trouvée à {SRC_IMG}")

ROCH_PRODUCTS = [
    {
        "name": "Climatiseur Split Roch 1.0 CV (9000 BTU) Simple Tropicalisé R410A",
        "power": "1.0 CV (9000 BTU)",
        "price": Decimal("137500"),
        "cost_price": Decimal("110000"),
        "stock": 12,
        "short_description": "Climatiseur split Roch 1.0 CV standard simple, excellent rapport qualité/prix à Bamako, gaz R410A écologique, kit de tuyaux inclus.",
        "description": "Le Climatiseur Split Mural Roch 1.0 CV Simple (9000 BTU) est la solution la plus économique et fiable pour équiper une chambre ou un bureau à Bamako. Compresseur tropicalisé puissant, soufflage d'air frais immédiat, gaz réfrigérant écologique R410A. Livré complet avec unité intérieure blanche compacte, unité extérieure protégée contre la corrosion, couronne de tuyauterie cuivre isolée, tuyau d'évacuation et télécommande.",
        "specifications": {
            "Marque": "Roch",
            "Modèle": "RAC Series Standard",
            "Type": "Climatiseur Split Mural Simple",
            "Capacité": "1.0 CV (9000 BTU)",
            "Gaz réfrigérant": "R410A respectueux de l'environnement",
            "Climat": "Tropicalisé T1/T3 résistant fortes chaleurs",
            "Accessoires inclus": "Kit complet de tuyaux cuivre, câble, évacuation, télécommande",
            "Surface conseillée": "12 à 18 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Roch 1.5 CV (12000 BTU) Simple Tropicalisé R410A",
        "power": "1.5 CV (12000 BTU)",
        "price": Decimal("150000"),
        "cost_price": Decimal("120000"),
        "stock": 15,
        "short_description": "Climatiseur split Roch 1.5 CV simple standard, le grand classique accessible pour les salons maliens, gaz R410A.",
        "description": "Le Climatiseur Split Mural Roch 1.5 CV Simple (12000 BTU) combine une puissance frigorifique généreuse et un tarif ultra-compétitif. Parfait pour les salons et chambres principales de 18 à 28 m². Compresseur robuste conçu pour affronter les températures caniculaires sans surchauffe. Livré avec son kit de tuyauterie d'installation complet.",
        "specifications": {
            "Marque": "Roch",
            "Modèle": "RAC Series 12K Standard",
            "Type": "Climatiseur Split Mural Simple",
            "Capacité": "1.5 CV (12000 BTU)",
            "Gaz réfrigérant": "R410A écologique",
            "Accessoires inclus": "Couronne tuyaux cuivre + télécommande",
            "Surface conseillée": "18 à 28 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    }
]

print("Insertion des 2 modèles Roch Simple...")

for idx, pdata in enumerate(ROCH_PRODUCTS, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-RCH-{idx:04d}"
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": cat_clim,
            "brand": brand_roch,
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
    rel_path = f"products/{roch_img_name}"
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
    print(f"[{idx}/2] OK: {product.name} | Prix Vente: {product.price:,} F | Prix Achat: {product.cost_price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")

print("\nPack Roch Simple importé avec succès !")
