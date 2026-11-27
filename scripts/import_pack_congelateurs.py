import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
django.setup()

from shop.models import Category, Brand, Product, ProductImage
from django.utils.text import slugify

# S'assurer que les catégories existent
cat_parent, _ = Category.objects.get_or_create(
    slug='refrigerateurs-congelateurs',
    defaults={
        'name': 'Réfrigérateurs & Congélateurs',
        'description': 'Réfrigérateurs combinés, américains et congélateurs haute performance pour Bamako et le Mali.'
    }
)

cat_congelateurs, _ = Category.objects.get_or_create(
    slug='congelateurs-verticaux',
    defaults={
        'name': 'Congélateurs Verticaux',
        'parent': cat_parent,
        'description': 'Congélateurs armoires et verticaux à tiroirs/étagères multiples, classe tropicalisée T pour le Mali.'
    }
)

brands_data = {
    'East Point': 'east-point',
    'Victoria': 'victoria',
    'LG': 'lg',
    'Sharp': 'sharp',
    'Roch': 'roch',
    'Étoile': 'etoile',
    'Solstar': 'solstar',
}

brands = {}
for name, slug in brands_data.items():
    b, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name, 'is_active': True})
    brands[name] = b

pack_products = [
    {
        'brand': 'East Point',
        'name': 'Congélateur Vertical East Point 245 Litres - 7 Étagères Tiroirs',
        'sku': 'ONZ-CONG-EASTP-245L',
        'price': 260000,
        'sale_price': 245000,
        'short_description': 'Congélateur vertical East Point 245L avec 7 compartiments de rangement ergonomiques. Froid renforcé tropicalisé, idéal pour stocker viandes, poissons et légumes en toute sérénité à Bamako.',
        'description': """Le **Congélateur Vertical East Point 245 Litres (7 Étagères)** est la solution idéale pour les familles et commerçants à la recherche d'une organisation parfaite et d'une congélation rapide.

### Points forts :
- **Volume utile** : 245 Litres optimisés.
- **Organisation** : 7 compartiments / étagères spacieux facilitant le tri sans perte d'air froid à l'ouverture.
- **Tropicalisé Climat T** : Fonctionne parfaitement même sous les fortes chaleurs de Bamako (> 43°C).
- **Économie d'énergie** : Compresseur basse consommation silencieux et gaz écologique R600a.
- **Sécurité** : Maintien du froid prolongé en cas de coupure de courant.
- **Garantie** : 12 Mois avec service après-vente Onizuka Shop Bamako Dibidani.""",
        'specs': {
            'Marque': 'East Point',
            'Type': 'Congélateur Vertical Armoire',
            'Capacité': '245 Litres',
            'Nombre d’étagères / tiroirs': '7 compartiments ergonomiques',
            'Classe climatique': 'T (Tropicalisé jusqu’à 43°C)',
            'Gaz réfrigérant': 'R600a Éco-énergétique',
            'Consommation': 'Basse consommation A+',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.41.44.jpeg',
            'whatsapp_image_2026-11-27_at_11.41.46.jpeg'
        ]
    },
    {
        'brand': 'Victoria',
        'name': 'Congélateur Vertical Victoria 300 Litres Grande Taille - 9 Étagères',
        'sku': 'ONZ-CONG-VICT-300L',
        'price': 385000,
        'sale_price': None,
        'short_description': 'Grand congélateur armoire Victoria 300L avec 9 étagères transparentes grand format. Capacité XXL, congélation express et design ultra-robuste.',
        'description': """Le **Congélateur Vertical Victoria 300 Litres (Grande Taille - 9 Étagères)** offre un volume massif pour les grandes familles et les professionnels de la restauration.

### Points forts :
- **Capacité géante** : 300 Litres réels pour stocker toutes vos provisions mensuelles.
- **9 Étagères et tiroirs amovibles** : Visibilité instantanée de vos aliments et gain de temps maximal.
- **Compresseur Tropicalisé Heavy-Duty** : Conçu pour supporter les variations de tension et les températures extrêmes.
- **Finition Inox Satinée** : Design moderne et résistant aux traces.
- **Garantie** : 12 Mois Onizuka Shop Grand Marché de Bamako.""",
        'specs': {
            'Marque': 'Victoria',
            'Type': 'Congélateur Armoire Grande Capacité',
            'Capacité': '300 Litres XXL',
            'Nombre d’étagères / tiroirs': '9 grands compartiments',
            'Classe climatique': 'T (Tropicalisé spécial Bamako)',
            'Gaz réfrigérant': 'R600a',
            'Finition': 'Inox haute résistance',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.44.27.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.27_1.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.29.jpeg'
        ]
    },
    {
        'brand': 'LG',
        'name': 'Congélateur Vertical LG Smart Inox - 6 Étagères Haute Précision',
        'sku': 'ONZ-CONG-LG-6ET',
        'price': 270000,
        'sale_price': None,
        'short_description': 'Congélateur vertical LG avec compresseur Smart Inverter durable et silencieux. 6 étagères de conservation optimale avec technologie anti-givre et froid uniforme.',
        'description': """Bénéficiez de la fiabilité légendaire de la marque **LG** avec ce **Congélateur Vertical Inox 6 Étagères**. 

### Points forts :
- **Technologie LG** : Refroidissement puissant et uniforme sur chaque niveau.
- **6 Compartiments renforcés** : Charnières et clayettes en verre trempé/tiroirs renforcés.
- **Compresseur Smart Silencieux** : Réduction substantielle de la facture d'électricité EDM.
- **Finition Premium Inox** : Résistance anti-rouille et esthétique irréprochable.
- **Garantie** : 12 Mois Onizuka Shop avec assistance express sur WhatsApp (+223 92 67 37 99).""",
        'specs': {
            'Marque': 'LG',
            'Type': 'Congélateur Vertical Inox',
            'Nombre d’étagères / tiroirs': '6 compartiments grande résistance',
            'Technologie': 'Smart Inverter Compresseur',
            'Classe climatique': 'T (Tropicalisé)',
            'Finition': 'Inox Anti-traces Platinum Silver',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.44.30.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.31.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.31_1.jpeg'
        ]
    },
    {
        'brand': 'Sharp',
        'name': 'Congélateur Vertical Sharp FR-495 Grande Capacité - 10 Étagères',
        'sku': 'ONZ-CONG-SHARP-FR495',
        'price': 425000,
        'sale_price': None,
        'short_description': 'Le roi des congélateurs verticaux : Sharp FR-495 avec 10 étagères ultra-spacieuses. Froid ventilé puissant, poignée ergonomique et robustesse japonaise garantie.',
        'description': """Le **Sharp FR-495** est le modèle très haut de gamme le plus recherché au Mali. Avec ses **10 étagères indépendantes**, il offre une capacité de rangement inégalée.

### Points forts :
- **Référence officielle** : Sharp FR-495 original.
- **10 Étagères / Tiroirs XL** : Compartimentation complète viandes, poissons, jus, glaçons et légumes.
- **Refroidissement Express** : Congélation ultra-rapide préservant la fraîcheur et les nutriments de vos aliments.
- **Joint antibactérien & isolation thermique renforcée** : Garde le froid intact plus de 24h sans électricité.
- **Garantie** : 12 Mois Onizuka Shop.""",
        'specs': {
            'Marque': 'Sharp',
            'Modèle': 'FR-495 Japan Technology',
            'Type': 'Congélateur Armoire Grande Capacité',
            'Nombre d’étagères / tiroirs': '10 tiroirs XL indépendants',
            'Refroidissement': 'Froid Express ventilé Multi-Air Flow',
            'Classe climatique': 'T (Tropicalisé)',
            'Isolation': 'Super Isotherme anti-coupure',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.48.18.jpeg',
            'whatsapp_image_2026-11-27_at_11.48.19.jpeg'
        ]
    },
    {
        'brand': 'Roch',
        'name': 'Congélateur Vertical Roch 212 Litres - 8 Étagères Pratiques',
        'sku': 'ONZ-CONG-ROCH-212L',
        'price': 275000,
        'sale_price': None,
        'short_description': 'Congélateur vertical Roch 212L équipé de 8 compartiments. Encombrement compact au sol pour un volume intérieur exceptionnel, idéal pour cuisine moderne.',
        'description': """Le **Congélateur Vertical Roch 212 Litres (8 Étagères)** allie compacité extérieure et générosité intérieure.

### Points forts :
- **Volume** : 212 Litres nets.
- **8 Compartiments** : Idéal pour un rangement facile et un accès direct sans fouiller.
- **Basse consommation** : Classe énergétique performante pour une utilisation continue sans surcoût.
- **Thermostat réglable** : Ajustez la puissance de froid selon vos besoins.
- **Garantie** : 12 Mois Onizuka Shop.""",
        'specs': {
            'Marque': 'Roch',
            'Capacité': '212 Litres',
            'Nombre d’étagères / tiroirs': '8 compartiments transparents',
            'Thermostat': 'Réglable multi-positions',
            'Classe climatique': 'T (Tropicalisé)',
            'Gaz réfrigérant': 'R600a',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.49.26.jpeg',
            'whatsapp_image_2026-11-27_at_11.49.26_1.jpeg'
        ]
    },
    {
        'brand': 'Étoile',
        'name': 'Congélateur Vertical Étoile 220 Litres - 8 Étagères',
        'sku': 'ONZ-CONG-ETOILE-220L',
        'price': 260000,
        'sale_price': None,
        'short_description': 'Congélateur vertical Étoile 220L 8 étagères. Fiable, robuste et parfaitement adapté au réseau électrique et aux conditions climatiques du Mali.',
        'description': """Le **Congélateur Vertical Étoile 220 Litres (8 Étagères)** offre le meilleur rapport qualité/prix de sa catégorie sur le marché de Bamako.

### Points forts :
- **Capacité** : 220 Litres bien compartimentés.
- **8 Étagères** : Tiroirs ergonomiques glissant facilement.
- **Froid Tropicalisé** : Refroidissement continu et silencieux.
- **Pieds réglables & porte réversible** : Installation facile dans tous les intérieurs.
- **Garantie** : 12 Mois Onizuka Shop.""",
        'specs': {
            'Marque': 'Étoile',
            'Capacité': '220 Litres',
            'Nombre d’étagères / tiroirs': '8 étagères à tiroirs',
            'Classe climatique': 'T (Tropicalisé)',
            'Consommation': 'Économique basse tension',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.51.50.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.50_1.jpeg'
        ]
    },
    {
        'brand': 'Solstar',
        'name': 'Congélateur Vertical Solstar Inox - 8 Étagères Robuste',
        'sku': 'ONZ-CONG-SOLSTAR-8ET',
        'price': 269000,
        'sale_price': None,
        'short_description': 'Congélateur vertical Solstar 8 étagères avec compresseur tropicalisé et carrosserie anti-corrosion. Spécialement conçu pour une endurance maximale.',
        'description': """Marque reconnue pour sa durabilité en Afrique de l'Ouest, **Solstar** propose ici un **Congélateur Vertical 8 Étagères** performant et robuste.

### Points forts :
- **8 Tiroirs de rangement** : Capacité optimale pour un stockage familial complet.
- **Compresseur Tropicalisé T** : Résiste aux fortes chaleurs et variations de courant.
- **Gaz écologique** : Respectueux de l'environnement et économe en énergie.
- **Finition Inox brossé** : Élégant et facile à nettoyer.
- **Garantie** : 12 Mois Onizuka Shop.""",
        'specs': {
            'Marque': 'Solstar',
            'Type': 'Congélateur Vertical Tropicalisé',
            'Nombre d’étagères / tiroirs': '8 tiroirs spacieux',
            'Classe climatique': 'T (Tropicalisé)',
            'Finition': 'Inox brossé anti-corrosion',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.51.51.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.51_1.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.51_2.jpeg'
        ]
    },
    {
        'brand': 'Sharp',
        'name': 'Congélateur Vertical Sharp Silver Premium - 8 Étagères',
        'sku': 'ONZ-CONG-SHARP-8ET',
        'price': 325000,
        'sale_price': None,
        'short_description': 'Congélateur vertical Sharp 8 étagères finition Silver luxe. Technologie japonaise de congélation rapide, silence de fonctionnement et économie d’énergie.',
        'description': """Le **Congélateur Vertical Sharp Silver 8 Étagères** combine l'excellence technologique de Sharp et un design moderne raffiné.

### Points forts :
- **Qualité de fabrication Sharp** : Matériaux de premier choix et isolation haute densité.
- **8 Compartiments ergonomiques** : Rangement clair et conservation longue durée sans givre excessif.
- **Super Freezing** : Touche de congélation accélérée pour les arrivages de denrées fraîches.
- **Compresseur tropicalisé certifié** : Longévité assurée dans toutes les conditions au Mali.
- **Garantie** : 12 Mois Onizuka Shop Bamako.""",
        'specs': {
            'Marque': 'Sharp',
            'Type': 'Congélateur Vertical Premium Silver',
            'Nombre d’étagères / tiroirs': '8 compartiments ergonomiques',
            'Technologie': 'Japan Quality Super Freezing',
            'Classe climatique': 'T (Tropicalisé certifié)',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.51.52.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.53.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.54.jpeg'
        ]
    }
]

created_count = 0
updated_count = 0

for item in pack_products:
    brand = brands[item['brand']]
    slug = slugify(item['name'])
    
    prod, created = Product.objects.update_or_create(
        sku=item['sku'],
        defaults={
            'name': item['name'],
            'slug': slug,
            'category': cat_congelateurs,
            'brand': brand,
            'price': item['price'],
            'sale_price': item['sale_price'],
            'short_description': item['short_description'],
            'description': item['description'],
            'specifications': item['specs'],
            'is_active': True,
            'is_featured': True,
            'stock': 10,
        }
    )
    
    # Nettoyer et réassigner les images de la galerie
    ProductImage.objects.filter(product=prod).delete()
    for idx, img_name in enumerate(item['images']):
        rel_path = f"products/congelateurs/{img_name}"
        ProductImage.objects.create(
            product=prod,
            image=rel_path,
            alt_text=f"{prod.name} - Vue {idx+1}",
            is_primary=(idx == 0),
            order=idx
        )
    
    if created:
        created_count += 1
        print(f"[+] Créé : {prod.name} | Prix : {prod.price:,} FCFA | Promo: {prod.sale_price} | SKU: {prod.sku}")
    else:
        updated_count += 1
        print(f"[*] Mis à jour : {prod.name} | Prix : {prod.price:,} FCFA | Promo: {prod.sale_price} | SKU: {prod.sku}")

print(f"\nTerminé avec succès ! {created_count} créés, {updated_count} mis à jour.")
