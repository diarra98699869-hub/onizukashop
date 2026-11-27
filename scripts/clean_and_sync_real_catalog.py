"""
Nettoyage et synchronisation stricte du VRAI catalogue d'Onizouka Shop (78 produits réels uniquement).
- Supprime tous les produits et catégories de démonstration / stock photos.
- Conserve et verrouille les 78 produits authentiques d'Onizouka Shop (Climatiseurs, Congélateurs Coffres, Congélateurs Verticaux, Vitrines).
- Lie toutes les photos WebP brutes sans aucun rognage (100% plein cadre).
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

from django.db import transaction
from shop.models import Category, Brand, Product, ProductImage

MEDIA_ROOT = BASE_DIR / 'media'
FIXTURE_PATH = BASE_DIR / 'fixtures' / 'real_catalog_78.json'

def sync_real_catalog():
    print("=== SYNCHRONISATION DU VRAI CATALOGUE ONIZOUKA SHOP (78 PRODUITS) ===")
    
    if not FIXTURE_PATH.exists():
        print("❌ Fichier real_catalog_78.json introuvable.")
        return

    with open(FIXTURE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    real_skus = set(item['fields']['sku'] for item in data if item['model'] == 'shop.product')

    with transaction.atomic():
        # 1. Supprimer tous les produits qui ne font pas partie des 78 vrais
        deleted_prods, _ = Product.objects.exclude(sku__in=real_skus).delete()
        print(f"🗑️ {deleted_prods} éléments démo supprimés.")

        # 2. Supprimer les catégories démo étrangères
        demo_slugs = ['televiseurs', 'cuisinieres', 'petit-electromenager', 'meubles-mobilier', 'decoration-luminaires', 'refrigerateurs']
        deleted_cats, _ = Category.objects.filter(slug__in=demo_slugs).delete()
        print(f"🗑️ {deleted_cats} catégories démo supprimées.")

        # 3. Supprimer les marques démo sans produits
        Brand.objects.filter(products__isnull=True).delete()

        # 4. S'assurer que les 78 produits réels sont bien dans la base avec leurs catégories et marques
        cat_map = {}
        for item in data:
            if item['model'] == 'shop.category':
                pk = item['pk']
                f = item['fields']
                cat, _ = Category.objects.get_or_create(
                    slug=f['slug'],
                    defaults={
                        'name': f['name'],
                        'description': f.get('description', ''),
                        'icon': f.get('icon', ''),
                        'order': f.get('order', 0),
                        'is_active': True,
                    }
                )
                cat_map[pk] = cat

        brand_map = {}
        for item in data:
            if item['model'] == 'shop.brand':
                pk = item['pk']
                f = item['fields']
                brand, _ = Brand.objects.get_or_create(
                    slug=f['slug'],
                    defaults={
                        'name': f['name'],
                        'description': f.get('description', ''),
                        'is_active': True,
                    }
                )
                brand_map[pk] = brand

        # Gérer la parenté de catégories réelles
        for item in data:
            if item['model'] == 'shop.category' and item['fields'].get('parent'):
                parent_pk = item['fields']['parent']
                child_cat = cat_map.get(item['pk'])
                parent_cat = cat_map.get(parent_pk)
                if child_cat and parent_cat and child_cat.parent != parent_cat:
                    child_cat.parent = parent_cat
                    child_cat.save()

        Category.objects.rebuild()

        prod_map = {}
        for item in data:
            if item['model'] == 'shop.product':
                f = item['fields']
                cat = cat_map.get(f['category'])
                brand = brand_map.get(f['brand'])
                if not cat or not brand:
                    continue

                prod, created = Product.objects.update_or_create(
                    sku=f['sku'],
                    defaults={
                        'name': f['name'],
                        'slug': f['slug'],
                        'category': cat,
                        'brand': brand,
                        'price': f['price'],
                        'sale_price': f.get('sale_price'),
                        'stock': f.get('stock', 10),
                        'track_stock': f.get('track_stock', True),
                        'is_featured': f.get('is_featured', False),
                        'is_new': f.get('is_new', False),
                        'is_active': True,
                        'description': f.get('description', ''),
                        'short_description': f.get('short_description', ''),
                        'specifications': f.get('specifications', {}),
                    }
                )
                prod_map[item['pk']] = prod

        # 5. Ré-associer les images
        for item in data:
            if item['model'] == 'shop.productimage':
                f = item['fields']
                prod = prod_map.get(f['product'])
                if not prod:
                    continue
                img_path = f['image']
                if (MEDIA_ROOT / img_path).exists():
                    ProductImage.objects.update_or_create(
                        product=prod,
                        image=img_path,
                        defaults={
                            'alt_text': f.get('alt_text', ''),
                            'is_primary': f.get('is_primary', False),
                            'order': f.get('order', 0),
                        }
                    )

    # 6. Lier les photos brutes sans rognage pour les 12 nouveaux produits
    from scripts.link_production_images import link_images
    link_images()

    total_prods = Product.objects.filter(is_active=True).count()
    print(f"\n✅ SUCCÈS : Le catalogue est propre avec exactement {total_prods} produits réels !")

if __name__ == '__main__':
    sync_real_catalog()
