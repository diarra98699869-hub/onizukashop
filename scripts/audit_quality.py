"""
Audit qualite - version ASCII pure
"""
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

import django
django.setup()

def ok(v): return '[OK]' if v else '[!!]'

print("=" * 60)
print("AUDIT QUALITE ONIZOUKA SHOP")
print("=" * 60)

# --- 1. BDD ---
print("\n[1] ETAT BASE DE DONNEES")
from shop.models import Product, Category, Brand
from orders.models import Order
from django.db.models import Avg, Max, Min

total = Product.objects.filter(is_active=True).count()
sans_image = Product.objects.filter(is_active=True, images__isnull=True).distinct().count()
sans_sku = Product.objects.filter(is_active=True, sku='').count()
rupture = Product.objects.filter(is_active=True, stock=0).count()
inactifs = Product.objects.filter(is_active=False).count()
sans_short = Product.objects.filter(is_active=True, short_description='').count()

print(f"  Produits actifs      : {total}")
print(f"  Produits inactifs    : {inactifs}")
print(f"  {ok(sans_image==0)} Sans image       : {sans_image}")
print(f"  {ok(sans_sku==0)} Sans SKU         : {sans_sku}")
print(f"  {ok(rupture==0)} En rupture stock : {rupture}")
print(f"  {ok(sans_short<5)} Sans resume      : {sans_short}")
print(f"  Categories           : {Category.objects.count()}")
print(f"  Marques              : {Brand.objects.count()}")
print(f"  Commandes totales    : {Order.objects.count()}")

stats = Product.objects.filter(is_active=True).aggregate(
    moy=Avg('price'), mx=Max('price'), mn=Min('price')
)
print(f"  Prix moyen  : {int(stats['moy'] or 0)} FCFA")
print(f"  Prix mini   : {int(stats['mn'] or 0)} FCFA")
print(f"  Prix maxi   : {int(stats['mx'] or 0)} FCFA")

# --- 2. PERF PAGES ---
print("\n[2] PERFORMANCE PAGES (temps reponse)")
from django.test import Client

c = Client()

p = Product.objects.filter(is_active=True).first()
pages = [
    ('/', 'Accueil'),
    ('/catalogue/', 'Catalogue'),
    ('/recherche/?q=samsung', 'Recherche'),
    ('/panier/', 'Panier'),
    ('/facebook-catalog.xml', 'Flux Meta XML'),
]
if p:
    pages.append((p.get_absolute_url(), f'Fiche produit'))

for url, name in pages:
    t0 = time.time()
    try:
        res = c.get(url)
        ms = (time.time() - t0) * 1000
        s = res.status_code
        if s not in (200, 302):
            flag = f'[!!] HTTP {s}'
        elif ms > 2000:
            flag = '[!!] TRES LENT'
        elif ms > 1000:
            flag = '[~~] Acceptable'
        else:
            flag = '[OK] Rapide'
        print(f"  {flag:<16} {ms:6.0f}ms  | {name}")
    except Exception as e:
        print(f"  [!!] ERREUR {url}: {e}")

# --- 3. SQL ---
print("\n[3] REQUETES SQL (Accueil)")
from django.test.utils import override_settings
from django.db import reset_queries, connection

with override_settings(DEBUG=True):
    reset_queries()
    c.get('/')
    n = len(connection.queries)
    f = '[OK]' if n <= 20 else ('[~~]' if n <= 40 else '[!!]')
    print(f"  {f} Requetes SQL accueil : {n}")
    slow = [q for q in connection.queries if float(q['time']) > 0.05]
    print(f"  Requetes > 50ms        : {len(slow)}")
    for q in slow[:5]:
        print(f"    {q['time']}s | {q['sql'][:80]}...")

# --- 4. URLS CLES ---
print("\n[4] URLS ESSENTIELLES")
urls = [
    ('/sitemap.xml', 200, 'Sitemap XML SEO'),
    ('/facebook-catalog.xml', 200, 'Flux Facebook Catalog'),
    ('/catalogue/', 200, 'Catalogue'),
    ('/cgv/', 200, 'CGV'),
    ('/mentions-legales/', 200, 'Mentions legales'),
    ('/confidentialite/', 200, 'Confidentialite'),
    ('/livraison-garantie/', 200, 'Livraison et Garantie'),
    ('/contact/', 200, 'Contact'),
    ('/panier/', 200, 'Panier'),
    ('/gestion/', 302, 'Backoffice'),
]
for url, exp, name in urls:
    try:
        res = c.get(url, follow=False)
        ok_v = res.status_code == exp
        print(f"  {ok(ok_v)} HTTP {res.status_code} | {name} ({url})")
    except Exception as e:
        print(f"  [!!] ERREUR | {url} : {e}")

# --- 5. SECURITE ---
print("\n[5] SECURITE")
from django.conf import settings as s
checks = [
    ('SECRET_KEY non generique', 'dev-secret' not in s.SECRET_KEY),
    ('HTTPS proxy configure', hasattr(s, 'SECURE_PROXY_SSL_HEADER')),
    ('CSRF middleware actif', 'django.middleware.csrf.CsrfViewMiddleware' in s.MIDDLEWARE),
    ('Password validators (4)', len(s.AUTH_PASSWORD_VALIDATORS) >= 4),
    ('ALLOWED_HOSTS non *', s.ALLOWED_HOSTS != ['*'] or s.DEBUG),
    ('Security middleware', 'django.middleware.security.SecurityMiddleware' in s.MIDDLEWARE),
    ('Whitenoise (fichiers statiques)', 'whitenoise.middleware.WhiteNoiseMiddleware' in s.MIDDLEWARE),
    ('Sessions BDD configurees', 'django.contrib.sessions' in s.INSTALLED_APPS),
]
for name, val in checks:
    print(f"  {ok(val)} {name}")

# --- 6. BACKOFFICE ---
print("\n[6] BACKOFFICE - ShopSettings")
try:
    from backoffice.models import ShopSetting
    cfg = ShopSetting.objects.first()
    if cfg:
        print(f"  {ok(bool(cfg.site_name))} Nom boutique      : {cfg.site_name}")
        print(f"  {ok(bool(cfg.whatsapp_number))} Numero WhatsApp   : {cfg.whatsapp_number}")
        print(f"  {ok(bool(cfg.meta_pixel_id))} Meta Pixel ID     : {'Configure' if cfg.meta_pixel_id else 'NON configure'}")
        print(f"  {ok(bool(cfg.meta_domain_verification))} Domain verif Meta : {'Configure' if cfg.meta_domain_verification else 'NON configure'}")
        print(f"  {ok(bool(cfg.orange_money_number))} Orange Money      : {cfg.orange_money_number or 'Non configure'}")
        print(f"  {ok(bool(cfg.wave_number))} Wave              : {cfg.wave_number or 'Non configure'}")
    else:
        print("  [!!] Aucun ShopSetting configure !")
except Exception as e:
    print(f"  [!!] Erreur ShopSetting : {e}")

print("\n" + "=" * 60)
print("AUDIT TERMINE")
print("=" * 60)
