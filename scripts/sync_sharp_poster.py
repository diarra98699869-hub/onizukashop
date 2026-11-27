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

SRC_INVERTER_FLYER = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729561910_e085429b.jpg"
SRC_PROMO_POSTER = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729577438_2cd2c3fe.jpg"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Copier les deux images
dst_inverter_flyer = "sharp_inverter_r32_official.jpg"
dst_promo_poster = "sharp_promo_affiche_onizuka.jpg"

if os.path.exists(SRC_INVERTER_FLYER):
    shutil.copy2(SRC_INVERTER_FLYER, os.path.join(MEDIA_PRODUCTS_DIR, dst_inverter_flyer))
if os.path.exists(SRC_PROMO_POSTER):
    shutil.copy2(SRC_PROMO_POSTER, os.path.join(MEDIA_PRODUCTS_DIR, dst_promo_poster))

brand_sharp = Brand.objects.get(slug="sharp")
cat_clim = Category.objects.get(slug="climatiseurs")

# 2. Mettre à jour les prix de la gamme Sharp Simple selon l'affiche exacte
simple_updates = {
    "climatiseur-split-sharp-1-cv-9000-btu-simple-tropicalise": {"price": Decimal("155000"), "cost_price": Decimal("125000")},
    "climatiseur-split-sharp-15-cv-12000-btu-simple-tropicalise": {"price": Decimal("175000"), "cost_price": Decimal("140000")},
    "climatiseur-split-sharp-2-cv-18000-btu-simple-tropicalise": {"price": Decimal("260000"), "cost_price": Decimal("210000")},
}

for slug, pdata in simple_updates.items():
    try:
        p = Product.objects.get(slug=slug)
        p.price = pdata["price"]
        p.cost_price = pdata["cost_price"]
        p.save()
        print(f"Prix mis a jour Sharp Simple: {p.name} -> {p.price:,} F")
        
        # Ajouter l'affiche promo en image secondaire
        ProductImage.objects.get_or_create(
            product=p,
            image=f"products/{dst_promo_poster}",
            defaults={"is_primary": False, "order": 1, "alt_text": "Affiche Promo Officielle Onizuka Shop"}
        )
    except Product.DoesNotExist:
        print(f"Produit non trouve: {slug}")

# 3. Créer la gamme Sharp Inverter
SHARP_INVERTER = [
    {
        "name": "Climatiseur Split Sharp Inverter 1.0 CV (9000 BTU) Gaz R32",
        "power": "1.0 CV (9000 BTU)",
        "price": Decimal("230000"),
        "cost_price": Decimal("180000"),
        "stock": 10,
        "short_description": "Climatiseur split Sharp Inverter 1.0 CV, économie d'énergie de 40% à 60%, fonction générateur basse tension, gaz écologique R32.",
        "description": "Le Climatiseur Split Mural Sharp Inverter 1.0 CV (9000 BTU) intègre la prestigieuse technologie japonaise avancée Japan Technology. Grâce à son système Inverter intelligent, il réduit la consommation électrique de 40% à 60%. Dispose du mode Générateur (fonctionnement fluide même à faible courant électrique), du contrôle de précision de température I-FEEL, du refroidissement Turbo puissant et du gaz écologique R32. Échangeur avec revêtement anticorrosion longue durée.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Inverter Japan Technology",
            "Capacité": "1.0 CV (9000 BTU)",
            "Technologie compresseur": "Inverter Éco-Énergétique (40% à 60% d'économie)",
            "Mode Générateur": "Fonctionne à faible courant / basse tension",
            "Capteur de température": "I-FEEL (contrôle précis de confort)",
            "Gaz frigorigène": "R32 écologique",
            "Revêtement": "Anti-corrosion longue durée",
            "Surface conseillée": "12 à 18 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Sharp Inverter 1.5 CV (12000 BTU) Gaz R32",
        "power": "1.5 CV (12000 BTU)",
        "price": Decimal("255000"),
        "cost_price": Decimal("200000"),
        "stock": 12,
        "short_description": "Climatiseur split Sharp Inverter 1.5 CV, technologie japonaise intelligente, froid turbo, fonctionne sur groupe électrogène.",
        "description": "Le Climatiseur Split Mural Sharp Inverter 1.5 CV (12000 BTU) offre le parfait équilibre entre grande puissance frigorifique et économie d'électricité au quotidien. Parfait pour les salons et chambres principales de 18 à 28 m² à Bamako. Système Inverter intelligent, fonction I-FEEL, mode Turbo puissant et compatibilité générateur électrique.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Inverter Japan Technology 12K",
            "Capacité": "1.5 CV (12000 BTU)",
            "Technologie": "Inverter Éco-Énergétique",
            "Gaz": "R32",
            "Fonctions": "Turbo Cooling, Mode Générateur, I-FEEL, Revêtement anticorrosion",
            "Surface conseillée": "18 à 28 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split Sharp Inverter 2.0 CV (18000 BTU) Gaz R32",
        "power": "2.0 CV (18000 BTU)",
        "price": Decimal("370000"),
        "cost_price": Decimal("295000"),
        "stock": 8,
        "short_description": "Climatiseur split Sharp Inverter 2.0 CV très grand débit, technologie japonaise haut de gamme pour salons VIP et bureaux.",
        "description": "Le fleuron de la gamme Sharp Inverter : le modèle 2.0 CV (18000 BTU). Conçu pour refroidir rapidement et silencieusement de grands espaces jusqu'à 38 m² sans surcharger votre compteur électrique. Système intelligent de régulation thermique, compresseur tropicalisé et gaz R32.",
        "specifications": {
            "Marque": "Sharp",
            "Modèle": "Sharp Inverter Japan Technology 18K",
            "Capacité": "2.0 CV (18000 BTU)",
            "Technologie": "Inverter Haute Capacité",
            "Surface conseillée": "25 à 38 m²",
            "Gaz": "R32",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    }
]

print("\nInsertion de la gamme Sharp Inverter...")
for idx, pdata in enumerate(SHARP_INVERTER, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-SHPINV-{idx:04d}"
    
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
        product.save()

    # Image 1: Flyer Sharp Inverter R32
    ProductImage.objects.get_or_create(
        product=product,
        image=f"products/{dst_inverter_flyer}",
        defaults={"is_primary": True, "order": 0, "alt_text": f"{product.name} Fiche Technique Sharp"}
    )
    # Image 2: Affiche Promo Onizuka Shop avec les prix
    ProductImage.objects.get_or_create(
        product=product,
        image=f"products/{dst_promo_poster}",
        defaults={"is_primary": False, "order": 1, "alt_text": f"Affiche Promo Onizuka Shop {product.name}"}
    )

    margin = product.margin
    margin_pct = product.margin_percentage
    print(f"[Inverter {idx}] OK: {product.name} | Prix Vente: {product.price:,} F | Marge: +{margin:,} F (+{margin_pct}%)")

print("\nSynchronisation terminée avec succès !")
