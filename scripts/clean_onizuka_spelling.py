"""
Script de migration et de nettoyage textuel global :
Remplace toutes les occurrences de "Onizouka" / "ONIZOUKA" / "onizoukashop"
par l'orthographe officielle "Onizuka" / "ONIZUKA" / "onizukashop"
dans tous les modèles Django de la base de données.
"""
import os
import sys
from pathlib import Path

# Assure que la racine du projet est dans sys.path quel que soit l'environnement
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

import django
django.setup()

from django.contrib.auth.models import User
from shop.models import Product, Brand, ProductImage, Category
from orders.models import Coupon
from backoffice.models import ShopSetting
from allauth.account.models import EmailAddress


def clean_text(val):
    if not val or not isinstance(val, str):
        return val
    return val.replace('ONIZOUKA', 'ONIZUKA').replace('Onizouka', 'Onizuka').replace('onizoukashop', 'onizukashop').replace('onizouka', 'onizuka')


def run():
    print("--- Démarrage du nettoyage Onizouka -> Onizuka ---")
    
    # 1. Produits
    p_cnt = 0
    for p in Product.objects.all():
        ch = False
        if p.description and 'onizouka' in p.description.lower():
            p.description = clean_text(p.description)
            ch = True
        if p.short_description and 'onizouka' in p.short_description.lower():
            p.short_description = clean_text(p.short_description)
            ch = True
        if p.name and 'onizouka' in p.name.lower():
            p.name = clean_text(p.name)
            ch = True
        if p.specifications and isinstance(p.specifications, dict):
            new_specs = {}
            for k, v in p.specifications.items():
                k_new = clean_text(k)
                v_new = clean_text(v) if isinstance(v, str) else v
                new_specs[k_new] = v_new
            if new_specs != p.specifications:
                p.specifications = new_specs
                ch = True
        elif p.specifications and isinstance(p.specifications, str):
            if 'onizouka' in p.specifications.lower():
                p.specifications = clean_text(p.specifications)
                ch = True
        if ch:
            p.save()
            p_cnt += 1
    print(f"-> Produits mis à jour : {p_cnt}")

    # 2. Marques
    b_cnt = 0
    for b in Brand.objects.all():
        ch = False
        if b.name and 'onizouka' in b.name.lower():
            b.name = clean_text(b.name)
            ch = True
        if b.description and 'onizouka' in b.description.lower():
            b.description = clean_text(b.description)
            ch = True
        if ch:
            b.save()
            b_cnt += 1
    print(f"-> Marques mises à jour : {b_cnt}")

    # 3. Images produits (alt_text)
    pi_cnt = 0
    for pi in ProductImage.objects.filter(alt_text__icontains='onizouka'):
        pi.alt_text = clean_text(pi.alt_text)
        pi.save(update_fields=['alt_text'])
        pi_cnt += 1
    print(f"-> Textes alternatifs images : {pi_cnt}")

    # 4. Coupons
    for c in Coupon.objects.filter(code__icontains='onizouka'):
        c.code = clean_text(c.code)
        c.save(update_fields=['code'])

    # 5. Paramètres de la boutique
    for s in ShopSetting.objects.all():
        ch = False
        for f in ['site_name', 'company_name', 'email_contact', 'email_orders']:
            val = getattr(s, f, '')
            if val and 'onizouka' in val.lower():
                setattr(s, f, clean_text(val))
                ch = True
        if ch:
            s.save()
    print("-> Paramètres ShopSetting mis à jour.")

    # 6. Utilisateurs & Emails
    for u in User.objects.filter(username='admin_onizouka'):
        u.username = 'admin_onizuka'
        u.email = 'direction@onizukashop.com'
        u.save()
    for u in User.objects.filter(last_name__icontains='onizouka'):
        u.last_name = clean_text(u.last_name)
        u.save()
    for u in User.objects.filter(email__icontains='onizoukashop'):
        u.email = clean_text(u.email)
        u.save()

    for em in EmailAddress.objects.filter(email__icontains='onizoukashop'):
        em.email = clean_text(em.email)
        em.save()

    print("=== Nettoyage BDD terminé avec succès ! ===")


if __name__ == '__main__':
    run()
