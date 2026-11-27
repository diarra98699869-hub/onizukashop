"""
Script universel et sécurisé pour synchroniser l'intégralité des congélateurs sur la production (PostgreSQL)
Sans aucune erreur de clé dupliquée (évite loaddata et utilise update_or_create).
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

def run():
    print("==================================================================")
    print(" SYNCHRONISATION GLOBALE DU CATALOGUE CONGÉLATEURS SUR PRODUCTION ")
    print("==================================================================")
    
    scripts = [
        ("Fizzen Coffres (110L, 160L, 210L, 270L, 350L, 430L, 550L)", "scripts/import_congelateurs_horizontaux.py"),
        ("Roch Coffres (316L, 550L)", "scripts/import_roch_coffres.py"),
        ("Pearl & TMT Coffres (Pearl 375L, TMT 200L, TMT 288L)", "scripts/import_pearl_tmt_coffres.py"),
        ("Sharp Coffres (450L Réf 580, 520L Réf 660)", "scripts/import_sharp_coffres.py"),
        ("Telimani 212L", "scripts/import_telimani_212l.py"),
        ("NAFA, Telimani 650L & LG 345L (avec recadrage propre)", "scripts/import_nafa_telimani_lg.py"),
    ]
    
    for title, script_rel in scripts:
        print(f"\n---> Exécution : {title}...")
        script_path = BASE_DIR / script_rel
        if script_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("mod", script_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, 'run'):
                mod.run()
        else:
            print(f" [!] Script introuvable: {script_rel}")
            
    from shop.models import Product, Category
    cat_vert = Category.objects.filter(slug='congelateurs-verticaux').first()
    cat_horiz = Category.objects.filter(slug='congelateurs-horizontaux').first()
    cat_parent = Category.objects.filter(slug='refrigerateurs-congelateurs').first()
    
    print("\n==================================================================")
    print(" RÉSULTAT FINAL DE LA SYNCHRONISATION :")
    print("==================================================================")
    if cat_vert:
        print(f" • Congélateurs Verticaux : {cat_vert.products.filter(is_active=True).count()} produits actifs")
    if cat_horiz:
        print(f" • Congélateurs Horizontaux (Coffres) : {cat_horiz.products.filter(is_active=True).count()} produits actifs")
    if cat_parent:
        desc = cat_parent.get_descendants(include_self=True)
        tot = Product.objects.filter(category__in=desc, is_active=True).count()
        print(f" • Total Rayon Réfrigérateurs & Congélateurs : {tot} produits actifs")
    print(f" • Total global boutique : {Product.objects.filter(is_active=True).count()} produits actifs")
    print("==================================================================\n")

if __name__ == '__main__':
    run()
