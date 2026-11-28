import os
import sys
import django
from pathlib import Path

# Initialisation Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
django.setup()

from shop.models import Category, Product

def run():
    print("=== Configuration des Catégories Meubles Onizuka Shop ===")
    
    # 1. Catégorie parente principale
    parent, created = Category.objects.get_or_create(
        slug='meubles-armoires',
        defaults={
            'name': 'Meubles & Mobilier',
            'description': 'Mobilier de maison, chambre, salon, cuisine, bureau et jardin au Grand Marché de Bamako.',
            'is_active': True,
            'order': 5,
        }
    )
    if not created and parent.name != 'Meubles & Mobilier':
        parent.name = 'Meubles & Mobilier'
        parent.order = 5
        parent.save()
    print(f"Catégorie Parente : [{parent.id}] {parent.name} (slug={parent.slug})")

    # 2. Les 6 sous-catégories définies par le propriétaire
    subcats_data = [
        {
            'slug': 'chambre-a-coucher',
            'name': 'Chambre à Coucher',
            'description': 'Lits complets, lits simples, armoires & dressings, coiffeuses, commodes, coffres-forts, moquettes et décoration de chambre.',
            'order': 1,
            'icon': 'bed',
        },
        {
            'slug': 'salon-sejour',
            'name': 'Le Salon & Séjour',
            'description': 'Ensembles Meuble TV + Table basse, meubles TV, tables basses, fauteuils, canapés, commodes, tapis de salon et tableaux décoratifs.',
            'order': 2,
            'icon': 'chair',
        },
        {
            'slug': 'mobilier-cuisine',
            'name': 'Mobilier de Cuisine',
            'description': 'Placards de cuisine importés, îlots et buffets de rangement pour cuisine moderne.',
            'order': 3,
            'icon': 'countertops',
        },
        {
            'slug': 'bureaux-salons-attente',
            'name': 'Bureaux & Salons d\'Attente',
            'description': 'Salons d\'attente professionnels, fauteuils d\'accueil, tables de réunion et bureaux d\'entreprise.',
            'order': 4,
            'icon': 'business_center',
        },
        {
            'slug': 'mobilier-jardin-terrasse',
            'name': 'Jardin & Terrasse (Extérieur)',
            'description': 'Salons de jardin, ensembles de terrasse, fauteuils d\'extérieur et mobilier plein air.',
            'order': 5,
            'icon': 'deck',
        },
        {
            'slug': 'salle-de-bain-toilette',
            'name': 'Salle de Bain & Toilette',
            'description': 'Étagères de douche, meubles sous-vasque, rangements pour lave-linge et buanderie.',
            'order': 6,
            'icon': 'bathtub',
        },
    ]

    created_subcats = {}
    for data in subcats_data:
        subcat, c = Category.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'parent': parent,
                'description': data['description'],
                'order': data['order'],
                'icon': data['icon'],
                'is_active': True,
            }
        )
        if not c:
            subcat.name = data['name']
            subcat.parent = parent
            subcat.description = data['description']
            subcat.order = data['order']
            subcat.icon = data['icon']
            subcat.is_active = True
            subcat.save()
        created_subcats[data['slug']] = subcat
        status = "Créée" if c else "Mise à jour"
        print(f"  -> {status} : [{subcat.id}] {subcat.name} (parent={subcat.parent.name})")

    # 3. Réassigner les armoires existantes à "Chambre à Coucher"
    chambre_cat = created_subcats['chambre-a-coucher']
    armoires = Product.objects.filter(
        name__icontains='armoire'
    )
    reassigned = 0
    for p in armoires:
        p.category = chambre_cat
        p.save(update_fields=['category'])
        reassigned += 1
        print(f"     * Produit réassigné à {chambre_cat.name} : {p.name}")

    print(f"\nTotal armoires classées dans « Chambre à Coucher » : {reassigned}")
    print("Reconstruction de l'arbre MPTT...")
    Category.objects.rebuild()
    print("Arbre MPTT reconstruit avec succès !")

if __name__ == '__main__':
    run()
