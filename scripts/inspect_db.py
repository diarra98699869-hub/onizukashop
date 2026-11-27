import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onizouka.settings")
import django
django.setup()

from shop.models import Category, Brand, Product

print("CATEGORIES:")
for c in Category.objects.all():
    print(f" - {c.id}: {c.name} (slug: {c.slug})")

print("\nBRANDS:")
for b in Brand.objects.all():
    print(f" - {b.id}: {b.name} (slug: {b.slug})")

print(f"\nPRODUCT COUNT: {Product.objects.count()}")
