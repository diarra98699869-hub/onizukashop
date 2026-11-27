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
    'Fizzen': 'fizzen',
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
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical East Point 245L avec 7 compartiments de rangement ergonomiques. Froid renforcé tropicalisé, idéal pour stocker viandes, poissons et légumes en toute sérénité à Bamako.',
        'description': "Le Congélateur Vertical East Point 245 Litres est spécialement conçu pour répondre aux besoins des foyers et commerces à Bamako. Doté de 7 tiroirs et étagères ergonomiques, il permet d'organiser facilement viandes, poissons et denrées surgelées sans mélanger les odeurs et sans perdre d'air froid à l'ouverture.\n\nSon moteur tropicalisé robuste assure un froid puissant et continu même pendant les fortes chaleurs. Très économe en électricité grâce à son gaz écologique R600a, il conserve parfaitement le froid plusieurs heures en cas de coupure de courant. Appareil garanti 1 an avec SAV officiel Onizuka Shop au Grand Marché de Bamako.",
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
        'is_eco_solar': False,
        'short_description': 'Grand congélateur armoire Victoria 300L avec 9 étagères transparentes grand format. Capacité XXL, congélation express et design ultra-robuste.',
        'description': "Idéal pour les grandes familles et les professionnels de la restauration, le Congélateur Vertical Victoria 300 Litres offre une capacité de stockage XXL avec ses 9 grands tiroirs transparents. Sa structure robuste en finition inox et son compresseur renforcé garantissent une congélation express et une longévité maximale face aux températures élevées de notre climat.\n\nChaque compartiment offre un accès direct et pratique à vos provisions quotidiennes. Appareil garanti 1 an avec livraison et suivi Onizuka Shop.",
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
            'whatsapp_image_2026-11-27_at_11.44.29.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.27_1.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.27.jpeg'
        ]
    },
    {
        'brand': 'LG',
        'name': 'Congélateur Vertical LG Smart Inox - 6 Étagères Haute Précision',
        'sku': 'ONZ-CONG-LG-6ET',
        'price': 270000,
        'sale_price': None,
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical LG avec compresseur Smart Inverter durable et silencieux. 6 étagères de conservation optimale avec technologie anti-givre et froid uniforme.',
        'description': "Alliez modernité et tranquillité d'esprit avec le Congélateur Vertical LG 6 étagères en finition Inox anti-traces. Équipé d'un compresseur Smart Inverter réputé pour sa durabilité et son silence de fonctionnement, il régule le froid de manière uniforme tout en réduisant considérablement la facture d'électricité.\n\nSes 6 tiroirs renforcés facilitent un tri soigné et rapide de vos aliments sans perte d'énergie. Appareil garanti 1 an par Onizuka Shop à Bamako.",
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
            'whatsapp_image_2026-11-27_at_11.44.31.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.30.jpeg',
            'whatsapp_image_2026-11-27_at_11.44.31_1.jpeg'
        ]
    },
    {
        'brand': 'Sharp',
        'name': 'Congélateur Vertical Sharp FR-495 Grande Capacité - 10 Étagères',
        'sku': 'ONZ-CONG-SHARP-FR495',
        'price': 425000,
        'sale_price': None,
        'is_eco_solar': False,
        'short_description': 'Le roi des congélateurs verticaux : Sharp FR-495 avec 10 étagères ultra-spacieuses. Froid ventilé puissant, poignée ergonomique et robustesse japonaise garantie.',
        'description': "Véritable référence du froid au Mali, le Congélateur Vertical Sharp FR-495 est le modèle haut de gamme le plus prisé. Avec ses 10 étagères indépendantes, il offre le plus grand nombre de compartiments pour ranger séparément poissons, viandes fraîches, sachets et légumes.\n\nSa technologie de congélation rapide Japan Technology et son isolation haute densité maintiennent vos aliments congelés pendant plus de 24 heures sans électricité. Appareil garanti 1 an Onizuka Shop.",
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
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical Roch 212L équipé de 8 compartiments. Encombrement compact au sol pour un volume intérieur exceptionnel, idéal pour cuisine moderne.',
        'description': "Le Congélateur Vertical Roch 212 Litres réunit compacité extérieure et générosité intérieure grâce à ses 8 compartiments bien agencés. Il s'intègre facilement dans toutes les cuisines tout en offrant un volume utile idéal pour le quotidien.\n\nSon thermostat réglable permet d'adapter la puissance de congélation à vos besoins, avec une consommation d'énergie maîtrisée et un entretien simplifié. Appareil garanti 1 an chez Onizuka Shop.",
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
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical Étoile 220L 8 étagères. Fiable, robuste et parfaitement adapté au réseau électrique et aux conditions climatiques du Mali.',
        'description': "Le Congélateur Vertical Étoile 220 Litres propose un excellent équilibre entre budget et performance. Avec ses 8 étagères à tiroirs coulissants, fini la corvée de fouiller dans un congélateur coffre : chaque aliment a sa place attitrée.\n\nSon système de refroidissement tropicalisé est parfaitement adapté au réseau électrique et aux conditions ambiantes de Bamako. Appareil garanti 1 an avec assistance Onizuka Shop.",
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
            'whatsapp_image_2026-11-27_at_11.51.50_1.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.51.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.51_1.jpeg'
        ]
    },
    {
        'brand': 'Solstar',
        'name': 'Congélateur Vertical Solstar Inox - 8 Étagères Robuste',
        'sku': 'ONZ-CONG-SOLSTAR-8ET',
        'price': 269000,
        'sale_price': None,
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical Solstar 8 étagères avec compresseur tropicalisé et carrosserie anti-corrosion. Spécialement conçu pour une endurance maximale.',
        'description': "Reconnue à travers l'Afrique de l'Ouest pour sa robustesse légendaire, la marque Solstar propose ce Congélateur Vertical 8 étagères à carrosserie inox brossé anti-corrosion.\n\nSpécialement renforcé pour résister aux aléas de tension et aux fortes températures de notre région, il assure une congélation homogène et rapide de tous vos produits frais. Appareil garanti 1 an Onizuka Shop Grand Marché de Bamako.",
        'specs': {
            'Marque': 'Solstar',
            'Type': 'Congélateur Vertical Tropicalisé',
            'Nombre d’étagères / tiroirs': '8 tiroirs spacieux',
            'Classe climatique': 'T (Tropicalisé)',
            'Finition': 'Inox brossé anti-corrosion',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'whatsapp_image_2026-11-27_at_11.51.51_2.jpeg',
            'whatsapp_image_2026-11-27_at_11.51.52.jpeg'
        ]
    },
    {
        'brand': 'Sharp',
        'name': 'Congélateur Vertical Sharp Silver Premium - 8 Étagères',
        'sku': 'ONZ-CONG-SHARP-8ET',
        'price': 325000,
        'sale_price': None,
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical Sharp 8 étagères finition Silver luxe. Technologie japonaise de congélation rapide, silence de fonctionnement et économie d’énergie.',
        'description': "Le Congélateur Vertical Sharp 8 étagères en finition Silver Premium combine l'élégance japonaise et une efficacité thermique remarquable.\n\nConçu avec une isolation isotherme renforcée et la fonction Super Freezing, il permet de surgeler rapidement les nouveaux arrivages sans faire remonter la température des compartiments voisins. Silencieux, économique et durable. Appareil garanti 1 an Onizuka Shop Bamako.",
        'specs': {
            'Marque': 'Sharp',
            'Modèle': 'FR-195X Japan Technology',
            'Type': 'Congélateur Vertical Premium Silver',
            'Nombre d’étagères / tiroirs': '8 compartiments ergonomiques',
            'Technologie': 'Japan Quality Super Freezing',
            'Classe climatique': 'T (Tropicalisé certifié)',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'sharp_fr195x_8et_face.jpg',
            'sharp_fr195x_8et_interieur.jpg',
            'whatsapp_image_2026-11-27_at_11.51.53.jpeg'
        ]
    },
    {
        'brand': 'Fizzen',
        'name': 'Congélateur Vertical Fizzen 220 Litres - 7 Étagères AC',
        'sku': 'ONZ-CONG-FIZZEN-220L-AC',
        'price': 238000,
        'sale_price': None,
        'is_eco_solar': False,
        'short_description': 'Congélateur vertical Fizzen 220L 7 étagères secteur AC. Compresseur tropicalisé haute performance -18°C, idéal pour un usage quotidien à Bamako.',
        'description': "Le Congélateur Vertical Fizzen 220 Litres (Alimentation Secteur AC) offre une excellente capacité de stockage avec ses 7 compartiments ergonomiques.\n\nConçu avec un compresseur tropicalisé robuste et la technologie Fast Freezing descendant jusqu'à -18°C, il conserve vos viandes, poissons et rafraîchissements en toute sécurité. Fonctionne sur le réseau électrique standard EDM avec une consommation optimisée. Appareil garanti 12 mois par Onizuka Shop.",
        'specs': {
            'Marque': 'Fizzen',
            'Modèle': 'FZ-220URFAC',
            'Type': 'Congélateur Vertical Armoire',
            'Alimentation': 'Courant Secteur AC 220V-240V / 50Hz',
            'Capacité': '220 Litres',
            'Nombre d’étagères / tiroirs': '7 compartiments',
            'Température': 'Fast Freezing jusqu’à -18°C',
            'Classe climatique': 'T (Tropicalisé)',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'fizzen_220l_ac_face.jpg',
            'fizzen_220l_ac_interieur.jpg'
        ]
    },
    {
        'brand': 'Fizzen',
        'name': 'Congélateur Vertical Fizzen 220 Litres Solaire Direct 24V - 7 Étagères DC',
        'sku': 'ONZ-CONG-FIZZEN-220L-DC',
        'price': 285000,
        'sale_price': None,
        'is_eco_solar': True,
        'short_description': 'Congélateur vertical Fizzen 220L 7 étagères 100% Solaire DC 24 Volts. Se branche directement sur batteries et panneaux sans onduleur pour zéro facture d’électricité.',
        'description': "Le Congélateur Vertical Fizzen 220 Litres Solaire DC 24 Volts est la solution idéale pour en finir définitivement avec les coupures de courant et les factures d'électricité à Bamako et en région.\n\nDoté d'un compresseur spécial courant continu DC 24V haut rendement, il se raccorde directement à votre installation solaire (batteries / régulateur) sans perte d'énergie. Ses 7 compartiments permettent une organisation parfaite de toutes vos denrées à une température constante de -18°C. Écologique, autonome et garanti 12 mois Onizuka Shop.",
        'specs': {
            'Marque': 'Fizzen',
            'Modèle': 'FZ-220URFDC Solar',
            'Type': 'Congélateur Vertical 100% Solaire Autonome',
            'Alimentation': 'Solaire Direct DC 24 Volts',
            'Capacité': '220 Litres',
            'Nombre d’étagères / tiroirs': '7 compartiments',
            'Température': 'Froid profond -18°C',
            'Technologie': 'Compresseur Solaire Basse Consommation',
            'Garantie': '12 Mois officiel Onizuka Shop'
        },
        'images': [
            'fizzen_220l_solaire_dc_face.jpg',
            'fizzen_220l_solaire_dc_interieur.jpg'
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
            'is_eco_solar': item.get('is_eco_solar', False),
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
