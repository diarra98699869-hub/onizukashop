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

SRC_IMG = r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded\media_1795729268223_4f36ba3d.jpg"
MEDIA_PRODUCTS_DIR = os.path.join(BASE_DIR, "media", "products")
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

# 1. Marque East Point
brand_ep, _ = Brand.objects.get_or_create(
    slug="east-point",
    defaults={
        "name": "East Point",
        "is_active": True,
        "description": "East Point - Climatiseurs Inverter et conventionnels tropicalisés haute performance pour l'Afrique de l'Ouest."
    }
)

cat_clim, _ = Category.objects.get_or_create(
    slug="climatiseurs",
    defaults={"name": "Climatiseurs", "is_active": True}
)

# Copier l'image source une fois sous un nom propre
main_img_name = "east_point_inverter_split_official.jpg"
main_img_path = os.path.join(MEDIA_PRODUCTS_DIR, main_img_name)
if os.path.exists(SRC_IMG):
    shutil.copy2(SRC_IMG, main_img_path)
    print(f"Image source copiée vers {main_img_path}")
else:
    print(f"Attention: Image source non trouvée à {SRC_IMG}")

EAST_POINT_PRODUCTS = [
    {
        "name": "Climatiseur Split East Point Inverter 1 CV (9000 BTU) Tropicalisé",
        "power": "1.0 CV (9000 BTU)",
        "tech": "Inverter Économie d'énergie",
        "price": Decimal("165500"),
        "cost_price": Decimal("135000"),
        "stock": 10,
        "short_description": "Climatiseur split East Point 1 CV Inverter, ultra silencieux, mode Turbo, économie d'énergie et mode Sleep.",
        "description": "Le Climatiseur Split Mural East Point 1 CV Inverter (9000 BTU) associe design épuré, fraîcheur instantanée et consommation électrique réduite. Équipé du compresseur Inverter avec 4 fonctions phares : Mode Turbo pour une descente rapide en température, fonctionnement ultra Silencieux, Mode Sleep pour des nuits paisibles et Économie d'énergie certifiée. Idéal pour chambres et bureaux de 12 à 18 m² à Bamako.",
        "specifications": {
            "Marque": "East Point",
            "Modèle": "EP Inverter Series",
            "Capacité": "1.0 CV (9000 BTU)",
            "Technologie": "Inverter Économie d'énergie",
            "Modes": "Turbo Cooling, Silencieux, Mode Nuit Sleep, Eco Mode",
            "Écran": "Affichage digital discret sur façade",
            "Surface conseillée": "12 à 18 m²",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split East Point Inverter 2 CV (18000 BTU) Tropicalisé",
        "power": "2.0 CV (18000 BTU)",
        "tech": "Inverter Économie d'énergie",
        "price": Decimal("250000"),
        "cost_price": Decimal("205000"),
        "stock": 10,
        "short_description": "Climatiseur split East Point 2 CV Inverter grand débit, mode Turbo, compresseur tropicalisé résistant.",
        "description": "Le Climatiseur Split Mural East Point 2 CV Inverter (18000 BTU) est calibré pour rafraîchir efficacement les salons, salles d'attente et grands bureaux professionnels de 25 à 35 m². Son système Inverter adapte sa puissance en temps réel pour supprimer les pics de consommation électrique. Façade blanc laqué moderne avec logo EP officiel, ailettes oscillantes motorisées et télécommande ergonomique incluse.",
        "specifications": {
            "Marque": "East Point",
            "Modèle": "EP Inverter Series 18K",
            "Capacité": "2.0 CV (18000 BTU)",
            "Technologie": "Inverter",
            "Surface recommandée": "25 à 35 m²",
            "Fonctions": "Turbo, Silencieux, Sleep, Économie d'énergie",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split East Point Inverter 2.5 CV (24000 BTU) Tropicalisé",
        "power": "2.5 CV (24000 BTU)",
        "tech": "Inverter Haute Puissance",
        "price": Decimal("310000"),
        "cost_price": Decimal("250000"),
        "stock": 8,
        "short_description": "Climatiseur split East Point 2.5 CV Inverter grande surface, débit d'air puissant, compresseur robuste.",
        "description": "Climatiseur Split East Point 2.5 CV Inverter (24000 BTU) conçu pour les très grandes pièces à vivre, duplex et bureaux de direction jusqu'à 48 m² à Bamako. Alliant la puissance brute d'un compresseur tropicalisé et la finesse de régulation Inverter, il maintient un froid homogène sans bruit assourdissant.",
        "specifications": {
            "Marque": "East Point",
            "Modèle": "EP Inverter Series 24K",
            "Capacité": "2.5 CV (24000 BTU)",
            "Technologie": "Inverter régulé",
            "Surface recommandée": "35 à 48 m²",
            "Fonctions": "Turbo Cooling, Filtre lavable, Mode Sleep, Eco",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    },
    {
        "name": "Climatiseur Split East Point 3.5 CV Tropicalisé Simple",
        "power": "3.5 CV (30000 BTU)",
        "tech": "Haute Puissance Tropicalisée Simple",
        "price": Decimal("460000"),
        "cost_price": Decimal("375000"),
        "stock": 5,
        "short_description": "Climatiseur split East Point 3.5 CV grande capacité, froid puissant instantané pour grands espaces et commerces.",
        "description": "Le Climatiseur Split Mural East Point 3.5 CV Simple (environ 30000 BTU) est une bête de puissance spécialement pensée pour les très grands volumes (salons majestueux, salles de réunion, commerces et espaces de réception). Moteur robuste tropicalisé T3 capable de fonctionner sans faiblir lors des canicules bamakoises de mars à mai. Souffle d'air longue distance et fiabilité éprouvée.",
        "specifications": {
            "Marque": "East Point",
            "Modèle": "EP Heavy Duty Series",
            "Capacité": "3.5 CV (~30000 BTU)",
            "Type": "Split Simple Tropicalisé Haute Puissance",
            "Surface recommandée": "45 à 65 m²",
            "Mode": "Turbo Grand Débit, Mode Nuit, Déshumidificateur",
            "Garantie": "1 an officiel Onizuka Shop"
        }
    }
]

print("Insertion des 4 modèles East Point...")

for idx, pdata in enumerate(EAST_POINT_PRODUCTS, start=1):
    slug = slugify(pdata["name"])
    sku = f"ONZ-EP-{idx:04d}"
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={
            "name": pdata["name"],
            "sku": sku,
            "category": cat_clim,
            "brand": brand_ep,
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

    # Rattacher l'image réelle
    rel_path = f"products/{main_img_name}"
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

print("\nPack East Point importé avec succès !")
