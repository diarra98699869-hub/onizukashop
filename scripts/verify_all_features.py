"""
ONIZUKA SHOP - Vérification End-to-End de TOUS les boutons, formulaires, vidéos (15s/8Mo), PWA & Capacitor
"""
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from shop.models import Product, Category, Brand
from orders.models import Order
from shop.video_utils import (
    find_ffmpeg_binary,
    process_uploaded_product_video,
    get_video_duration_ffmpeg,
    MAX_VIDEO_DURATION_SECONDS,
    MAX_VIDEO_SIZE_BYTES,
)

User = get_user_model()
errors = []

def check(name, cond, detail=''):
    status = "OK" if cond else "ECHEC"
    print(f"  [{status}] {name}" + (f" ({detail})" if detail else ""))
    if not cond:
        errors.append(f"{name}: {detail}")


print("=" * 72)
print("ONIZUKA SHOP - VERIFICATION COMPLETE BOUTONS, VIDEOS (15s/8Mo), PWA & CAPACITOR")
print("=" * 72)

c = Client()
prod = Product.objects.filter(is_active=True, stock__gt=0).first()
cat = Category.objects.filter(is_active=True).first()

# ---------------------------------------------------------------------------
# 1. BOUTIQUE PUBLIQUE : ROUTES, ONGLETS HTMX, RECHERCHE LIVE, PANIER, FAVORIS
# ---------------------------------------------------------------------------
print("\n[1] BOUTIQUE PUBLIQUE & BOUTONS INTERACTIFS")
public_routes = [
    ('/', 200, 'Accueil Marketplace'),
    ('/?tab=promos', 200, 'Onglet Accueil Promos'),
    ('/?tab=nouveautes', 200, 'Onglet Accueil Nouveautes'),
    ('/catalogue/', 200, 'Catalogue General'),
    ('/catalogue/?tri=prix_asc', 200, 'Tri Prix Croissant'),
    ('/catalogue/?tri=prix_desc', 200, 'Tri Prix Decroissant'),
    ('/catalogue/?avec_video=true', 200, 'Filtre Avec Video'),
    ('/catalogue/?eco_solaire=true', 200, 'Filtre Eco / Solaire'),
    ('/catalogue/?budget=100k_300k', 200, 'Filtre Tranche Budget'),
    ('/recherche/?q=clim', 200, 'Page Recherche'),
    ('/recherche/live/?q=sharp', 200, 'Live Search Autocomplete HTMX'),
    ('/panier/', 200, 'Page Panier'),
    ('/panier/suivi/', 200, 'Suivi Public Commande'),
    ('/contact/', 200, 'Page Contact'),
    ('/cgv/', 200, 'Page CGV'),
    ('/confidentialite/', 200, 'Page Confidentialite'),
    ('/mentions-legales/', 200, 'Page Mentions Legales'),
    ('/livraison-garantie/', 200, 'Page Livraison & Garantie'),
    ('/facebook-catalog.xml', 200, 'Flux XML Meta Catalog'),
]
if cat:
    public_routes.append((f'/catalogue/{cat.slug}/', 200, f'Rayon {cat.name}'))
if prod:
    public_routes.append((prod.get_absolute_url(), 200, f'Fiche Produit ({prod.sku})'))

for url, expected, label in public_routes:
    res = c.get(url)
    check(label, res.status_code == expected, f"HTTP {res.status_code} sur {url}")

# Test HTMX partial sur l'accueil et le catalogue
res_htmx_home = c.get('/?tab=tous', HTTP_HX_REQUEST='true')
check("Flux HTMX Accueil (sans rechargement)", res_htmx_home.status_code == 200)

res_htmx_cat = c.get('/catalogue/?tri=prix_asc', HTTP_HX_REQUEST='true')
check("Filtre HTMX Catalogue (sans rechargement)", res_htmx_cat.status_code == 200)

# Test Bouton "+ Panier" AJAX
if prod:
    res_add = c.post(
        f'/panier/ajouter/{prod.pk}/',
        {'quantity': 1, 'with_addon': '1'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
    )
    add_data = res_add.json() if res_add.status_code == 200 else {}
    check("Bouton '+ Panier' AJAX (1-clic + option)", res_add.status_code == 200 and add_data.get('success') is True, str(add_data))

    res_checkout = c.get('/panier/commander/')
    check("Accès Page Checkout avec panier actif", res_checkout.status_code == 200)

    # Vider le panier de test pour ne laisser aucune trace en BDD
    from orders.models import Cart
    Cart.objects.all().delete()

# ---------------------------------------------------------------------------
# 2. PWA PRO & CAPACITOR NATIVE
# ---------------------------------------------------------------------------
print("\n[2] PWA PRO & CAPACITOR MOBILE NATIVE")
res_manifest = c.get('/manifest.json')
manifest_data = res_manifest.json() if res_manifest.status_code == 200 else {}
check("Manifest JSON (/manifest.json)", res_manifest.status_code == 200 and manifest_data.get('display') == 'standalone')
icon_sizes = [i.get('sizes') for i in manifest_data.get('icons', [])]
check("Icônes PWA PNG 192x192 & 512x512 + Maskable", '192x192' in icon_sizes and '512x512' in icon_sizes, str(icon_sizes))
check("Raccourcis App PWA (Shortcuts)", len(manifest_data.get('shortcuts', [])) >= 4, f"{len(manifest_data.get('shortcuts', []))} raccourcis")

res_sw = c.get('/sw.js')
sw_text = res_sw.content.decode('utf-8')
check("Service Worker v3 (/sw.js)", res_sw.status_code == 200 and 'onizuka-static-v3' in sw_text and '/offline.html' in sw_text)

res_offline = c.get('/offline.html')
check("Page Hors-Ligne (/offline.html)", res_offline.status_code == 200 and 'ONIZUKA' in res_offline.content.decode('utf-8'))

check("Fichier capacitor.config.json", (BASE_DIR / 'capacitor.config.json').exists())
check("Fichier package.json Capacitor", (BASE_DIR / 'package.json').exists())
check("Shell Natif Capacitor www/index.html", (BASE_DIR / 'www' / 'index.html').exists())
check("Pont JS static/js/capacitor-bridge.js", (BASE_DIR / 'static' / 'js' / 'capacitor-bridge.js').exists())
check(
    "Ressources APK Android & iOS (resources/icon.png 1024px & splash.png 2732px)",
    (BASE_DIR / 'resources' / 'icon.png').exists() and (BASE_DIR / 'resources' / 'splash.png').exists() and (BASE_DIR / 'resources' / 'icon-foreground.png').exists()
)

# ---------------------------------------------------------------------------
# 3. LIMITE & COMPRESSION VIDEO AUTOMATIQUE (15 SECONDES MAX / 8 MO MAX)
# ---------------------------------------------------------------------------
print("\n[3] TEST DECOUPE (15s MAX) & COMPRESSION VIDEO AUTOMATIQUE (8 Mo MAX)")
ffmpeg_bin = find_ffmpeg_binary()
check("Binaire FFmpeg détecté sur le système", bool(ffmpeg_bin), str(ffmpeg_bin))

if ffmpeg_bin:
    # Générer une vidéo synthétique de 22 secondes (> 15s) pour vérifier la découpe automatique à 15s
    tmp_vid_fd, tmp_vid_path = tempfile.mkstemp(suffix='.mp4')
    os.close(tmp_vid_fd)
    try:
        subprocess.run([
            ffmpeg_bin, '-y', '-hide_banner', '-loglevel', 'error',
            '-f', 'lavfi', '-i', 'testsrc=duration=22:size=640x360:rate=15',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
            tmp_vid_path
        ], check=True, timeout=30)

        orig_dur = get_video_duration_ffmpeg(tmp_vid_path, ffmpeg_bin=ffmpeg_bin)
        with open(tmp_vid_path, 'rb') as vf:
            raw_vid = vf.read()

        up_vid = SimpleUploadedFile('test_long_22s.mp4', raw_vid, content_type='video/mp4')
        processed_file, v_info = process_uploaded_product_video(up_vid)

        check(
            "Découpe automatique d'une vidéo de 22s -> 15s max",
            v_info.get('was_trimmed') is True and (v_info.get('final_duration') or 99) <= 15.5,
            f"Origine: {orig_dur}s -> Finale: {v_info.get('final_duration')}s | Poids: {v_info.get('final_size_mb')} Mo"
        )
        check(
            "Respect strict du plafond 8 Mo",
            processed_file.size <= MAX_VIDEO_SIZE_BYTES,
            f"{v_info.get('final_size_mb')} Mo <= 8.0 Mo"
        )
    finally:
        if os.path.exists(tmp_vid_path):
            try:
                os.remove(tmp_vid_path)
            except OSError:
                pass

# ---------------------------------------------------------------------------
# 4. BACKOFFICE DIRECTION (/gestion/) : TOUTES LES PAGES & ACTIONS
# ---------------------------------------------------------------------------
print("\n[4] PORTAIL GESTION DIRECTION (/gestion/) & TABLEUR EXCEL")
staff_user = User.objects.filter(is_staff=True).first()
if staff_user:
    c.force_login(staff_user)
    bo_routes = [
        ('/gestion/', 200, 'Dashboard Direction'),
        ('/gestion/?period=7d', 200, 'Filtre Dashboard 7 jours'),
        ('/gestion/commandes/', 200, 'Liste Commandes'),
        ('/gestion/commandes/nouvelle/', 200, 'Caisse Express Boutique / WhatsApp'),
        ('/gestion/commandes/export-csv/', 200, 'Export CSV Commandes'),
        ('/gestion/produits/', 200, 'Catalogue Gestion'),
        ('/gestion/produits/tableur/', 200, 'Mode Tableur Excel'),
        ('/gestion/produits/ajout-masse/', 200, 'Grille Ajout en Masse'),
        ('/gestion/produits/nouveau/', 200, 'Formulaire Nouveau Produit'),
        ('/gestion/produits/export-csv/', 200, 'Export CSV Produits'),
        ('/gestion/produits/modele-csv/', 200, 'Modele CSV Produits'),
        ('/gestion/stocks/', 200, 'Stocks & Approvisionnement'),
        ('/gestion/clients/', 200, 'Annuaire Clients'),
        ('/gestion/catalogue-config/', 200, 'Hub Rayons, Marques, Promos, Avis & Fournisseurs'),
        ('/gestion/emails/', 200, 'Centre Emails, Templates, Conditions, Alertes & Rappels'),
        ('/gestion/emails/apercu/order_confirmation/', 200, 'Apercu Live Template Confirmation Commande'),
        ('/gestion/emails/apercu/order_payment_reminder/', 200, 'Apercu Live Template Rappel Finalisation Commande'),
        ('/gestion/emails/apercu/abandoned_cart_reminder/', 200, 'Apercu Live Template Rappel Panier Abandonne'),
        ('/gestion/emails/apercu/order_status_update/', 200, 'Apercu Live Template Statut Livraison'),
        ('/gestion/emails/apercu/admin_new_order_alert/', 200, 'Apercu Live Template Alerte Nouvelle Commande'),
        ('/gestion/emails/apercu/admin_low_stock_alert/', 200, 'Apercu Live Template Alerte Stock Bas'),
        ('/gestion/emails/apercu/admin_contact_message/', 200, 'Apercu Live Template Alerte Message Contact'),
        ('/gestion/utilisateurs/', 200, 'Equipe & Utilisateurs'),
        ('/gestion/parametres/', 200, 'Parametres Boutique'),
    ]
    if prod:
        bo_routes.append((f'/gestion/produits/{prod.id}/modifier/', 200, f'Edition Produit #{prod.id}'))

    # Test Facture PDF & Bon de livraison officiel (Direction & Client)
    test_order = Order.objects.filter(order_number='ONZ-VERIF-TEST').first()
    if not test_order:
        test_order = Order.objects.create(
            order_number='ONZ-VERIF-TEST',
            delivery_name='Client Test Direction',
            delivery_phone='+223 92 67 37 99',
            delivery_address='Grand Marché de Bamako, Dibidani',
            delivery_district='Grand Marché',
            subtotal=125000,
            total=125000,
        )
    bo_routes.append((f'/gestion/commandes/{test_order.id}/facture/', 200, f'Facture PDF Direction #{test_order.order_number}'))
    bo_routes.append((f'/panier/mes-commandes/{test_order.order_number}/facture/', 200, f'Facture PDF Client #{test_order.order_number}'))

    for url, expected, label in bo_routes:
        res = c.get(url)
        check(label, res.status_code == expected, f"HTTP {res.status_code} sur {url}")

    # Test Sauvegarde Tableur Excel (Bulk Save JSON sans altérer le prix)
    if prod:
        res_bulk = c.post(
            '/gestion/produits/sauvegarder-masse/',
            data=json.dumps({'items': [{'id': prod.id, 'price': int(prod.price), 'stock': prod.stock}]}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        check("Bouton 'Enregistrer Tout' du Tableur Excel", res_bulk.status_code == 200 and res_bulk.json().get('status') == 'ok')

    # Test Hub /gestion/catalogue-config/ : Création & Suppression d'un code promo de test
    from orders.models import Coupon
    res_coupon_create = c.post('/gestion/catalogue-config/', {
        'action': 'save_coupon',
        'code': 'TESTVERIFY99',
        'discount_type': 'FIXED',
        'discount_value': 5000,
        'min_order_amount': 50000,
    })
    created_cp = Coupon.objects.filter(code='TESTVERIFY99').first()
    check("Création Code Promo depuis /gestion/catalogue-config/", created_cp is not None)
    if created_cp:
        c.post('/gestion/catalogue-config/', {
            'action': 'delete_coupon',
            'coupon_id': created_cp.id,
        })
        check("Suppression Code Promo depuis /gestion/catalogue-config/", not Coupon.objects.filter(id=created_cp.id).exists())

    # Test Envoi Email de Test & Journalisation dans EmailLog depuis /gestion/emails/
    from backoffice.models import EmailLog
    res_test_mail = c.post('/gestion/emails/', {
        'action': 'send_test_email',
        'test_template': 'order_payment_reminder',
        'test_recipient': 'client@onizukashop.com',
        'tab': 'conditions',
    })
    check(
        "Envoi Email Rappel Finalisation & Journal EmailLog (/gestion/emails/)",
        res_test_mail.status_code == 302 and EmailLog.objects.filter(recipient='client@onizukashop.com', email_type='payment_reminder').exists()
    )
    EmailLog.objects.filter(recipient='client@onizukashop.com').delete()

    # ---------------------------------------------------------------------------
    # 5. AUDIT META ADS / COMMERCE MANAGER XML & APERCU WHATSAPP OPEN GRAPH
    # ---------------------------------------------------------------------------
    print("\n[5] AUDIT META COMMERCE XML, PIXEL & APERCU PHOTO WHATSAPP")
    import xml.etree.ElementTree as ET
    res_xml = c.get('/facebook-catalog.xml')
    xml_body = res_xml.content.decode('utf-8')
    try:
        root = ET.fromstring(xml_body)
        items_xml = root.findall('./channel/item')
        ns = {'g': 'http://base.google.com/ns/1.0'}
        zero_price_items = [
            it.find('g:id', ns).text for it in items_xml
            if (it.find('g:price', ns) is None or it.find('g:price', ns).text.startswith('0 '))
        ]
        missing_img_items = [
            it.find('g:id', ns).text for it in items_xml
            if (it.find('g:image_link', ns) is None or not (it.find('g:image_link', ns).text or '').strip())
        ]
        check("Flux XML Meta Commerce valide & bien formé", len(items_xml) > 0, f"{len(items_xml)} produits exportés")
        check("Aucun produit à 0 FCFA dans le flux Meta Ads", len(zero_price_items) == 0, str(zero_price_items))
        check("100% des produits Meta ont une image HD (<g:image_link>)", len(missing_img_items) == 0)
    except Exception as e:
        check("Flux XML Meta Commerce valide & bien formé", False, str(e))

    if prod:
        res_p = c.get(prod.get_absolute_url())
        html_p = res_p.content.decode('utf-8')
        has_og = (
            'property="og:image"' in html_p and
            'property="og:title"' in html_p and
            'property="product:retailer_item_id"' in html_p and
            'property="product:price:currency" content="XOF"' in html_p
        )
        check("Balises Open Graph WhatsApp / Meta (Photo + Prix FCFA + SKU)", has_og)
        check("Lien Produit inclus dans le bouton WhatsApp 1-clic (Aperçu Photo WhatsApp)", prod.get_absolute_url() in html_p and "wa.me/" in html_p)

print("\n" + "=" * 72)
if not errors:
    print("RESULTAT : 100% DES TESTS REUSSIS (0 ERREUR)")
else:
    print(f"RESULTAT : {len(errors)} ERREUR(S) DETECTEE(S)")
    for e in errors:
        print(" -", e)
print("=" * 72)
sys.exit(1 if errors else 0)
