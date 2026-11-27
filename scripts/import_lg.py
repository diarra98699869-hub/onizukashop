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

# 1. Marque LG et Catégorie Climatiseurs
brand_lg, _ = Brand.objects.get_or_create(
    slug="lg",
    defaults={"name": "LG Electronics", "is_active": True}
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

name = "Climatiseur Split Mural LG Dual Inverter 12000 BTU (1.5 CV) IBY13AN Gaz R32"
slug = slugify(name)
sku = "ONZ-LG-0001"

product, created = Product.objects.get_or_create(
    slug=slug,
    defaults={
        "name": name,
        "sku": sku,
        "category": cat_clim,
        "brand": brand_lg,
        "cost_price": None,
        "price": Decimal("0"),
        "sale_price": None,
        "stock": 5,
        "min_stock": 2,
        "track_stock": True,
        "is_eco_solar": False,
        "is_featured": True,
        "is_new": True,
        "is_active": True,
        "status": Product.Status.ACTIVE,
        "short_description": "Climatiseur Split LG Dual Inverter 1.5 CV (12000 BTU) modèle officiel IBY13AN JU1, gaz R32 nouvelle génération, compresseur tropicalisé économe.",
        "description": "Le Climatiseur Split Mural LG Dual Inverter 12000 BTU (1.5 CV), référence constructeur IBY13AN JU1, incarne la pointe de la technologie coréenne en climatisation résidentielle. Grâce à son compresseur LG Dual Inverter breveté, il assure un rafraîchissement rapide tout en diminuant la facture d'électricité jusqu'à 70%. Utilisant le fluide frigorigène écologique R32 à fort pouvoir thermique et faible impact environnemental. Livré complet dans son conditionnement d'origine avec unité intérieure ultra-design blanche, groupe compresseur extérieur renforcé et couronne de tuyaux en cuivre de raccordement pré-isolée.",
        "specifications": {
            "Marque": "LG Electronics",
            "Modèle": "IBY13AN JU1 / ATW08X7",
            "Puissance": "12000 BTU (1.5 Cheval)",
            "Technologie": "LG Dual Inverter (économies jusqu'à -70%)",
            "Gaz réfrigérant": "R32 écologique",
            "Alimentation": "220 V~ / 50 Hz",
            "Accessoires inclus": "Couronne de raccordement cuivre isolée + Télécommande LG",
            "Surface conseillée": "18 à 28 m²",
            "Garantie": "1 an Onizuka Shop"
        },
        "meta_title": f"{name} - Prix Bamako Mali | Onizuka Shop",
        "meta_description": "Climatiseur Split LG Dual Inverter 1.5 CV IBY13AN Gaz R32 disponible chez Onizuka Shop Grand Marché Bamako Dibidani."
    }
)

if not created:
    product.price = Decimal("0")
    product.cost_price = None
    product.save()

# Image LG
src_file = "WhatsApp Image 2026-11-26 at 20.21.58.jpeg"
src_path = os.path.join(SRC_DIR, src_file)
if os.path.exists(src_path):
    dst_file = "lg_dual_inverter_iby13an_1.jpeg"
    dst_path = os.path.join(MEDIA_PRODUCTS_DIR, dst_file)
    shutil.copy2(src_path, dst_path)
    
    rel_path = f"products/{dst_file}"
    pimg, img_created = ProductImage.objects.get_or_create(
        product=product,
        image=rel_path,
        defaults={
            "is_primary": True,
            "order": 0,
            "alt_text": f"{product.name} Onizuka Shop Grand Marché Bamako"
        }
    )
    if not pimg.is_primary:
        pimg.is_primary = True
        pimg.save()

print(f"Produit LG inséré avec succès : {product.name} (SKU: {product.sku})")
print(f"Prix de vente : {product.price} FCFA (En attente de modification par le propriétaire)")
print(f"Stock initial : {product.stock} unités | Image : {rel_path}")
