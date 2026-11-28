"""
Script d'importation du lot 2 de nouveautés :
1. Cuisinière 6 feux mix gaz et courant (340 000 FCFA)
2. Meuble TV avec support (32" à 55") Rolls-Royce (115 000 FCFA)
3. VTT Vélo Luta Super-Boss TLJ003-26 (85 000 FCFA - 4 coloris)
4. Réfrigérateur combiné Innova 150L IN-255 (185 000 FCFA)
5. Cuisinière mixte Kaysun 4 feux (2 gaz + 2 plaques élec) (185 000 FCFA)
6. Table à manger marbre 4 places contemporaine carrée (230 000 FCFA)
7. Réfrigérateur Étoile combiné 50x50 Turquie XRD-220 (130 000 FCFA)
8. Ventilateur à eau brumisateur géant 30 pouces Excellent (125 000 FCFA)
9. Table basse gigogne ronde 2 pièces avec tiroir cannelé (95 000 FCFA - 3 modèles)
10. Salle à manger 4 places luxe Chanel / Noyer verre trempé (260 000 FCFA - 2 finitions)
11. Table basse gigogne carrée 3 pièces métal doré & marbre/verre (74 000 FCFA - 3 finitions)
12. Table basse gigogne ronde 2 pièces bois noyer (59 000 FCFA)
13. Meuble TV avec support étirable prolongeable marbre crème (135 000 FCFA)
14. Ensemble Meuble TV + Table basse complet luxe marbre (375 000 FCFA - 3 modèles : A3, A7, A9)
15. Ensemble Meuble TV + Table basse complet marbre (190 000 FCFA - 4 modèles/coloris)
16. Ensemble Table complet luxe marbre pivotant / galbé (400 000 FCFA - 3 modèles : M31, M38, M56-150#)
"""

import os
import sys
import shutil
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')

import django
django.setup()

from django.utils.text import slugify
from shop.models import Category, Brand, Product, ProductImage

MEDIA_PRODUCTS = BASE_DIR / 'media' / 'products'
MEDIA_PRODUCTS.mkdir(parents=True, exist_ok=True)

USER_UPLOADED_DIR = Path(r"C:\Users\a\.gemini\antigravity\brain\507b0a9b-c11c-4a9e-a9ab-0b97eff9541e\.user_uploaded")

def copy_and_convert_image(src_name, dest_filename):
    src_path = USER_UPLOADED_DIR / src_name
    dest_path = MEDIA_PRODUCTS / dest_filename
    if src_path.exists():
        try:
            with Image.open(src_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=90, optimize=True)
            return f"products/{dest_filename}"
        except Exception as e:
            print(f"Erreur conversion {src_name}: {e}")
            shutil.copy2(src_path, dest_path)
            return f"products/{dest_filename}"
    else:
        print(f"Fichier source introuvable : {src_path}")
        return None

def get_or_create_cat(name, parent_slug=None, icon=None):
    slug = slugify(name)
    parent = None
    if parent_slug:
        parent = Category.objects.filter(slug=parent_slug).first()
    
    cat, created = Category.objects.get_or_create(
        slug=slug,
        defaults={
            'name': name,
            'parent': parent,
            'icon': icon or 'shopping-bag',
            'is_active': True,
        }
    )
    if not created and parent and cat.parent != parent:
        cat.parent = parent
        cat.save()
    return cat

def get_or_create_brand(name):
    slug = slugify(name)
    brand, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name})
    return brand

def create_product(data, image_sources=None):
    slug = slugify(data['name'])
    base_slug = slug
    idx = 1
    while Product.objects.filter(slug=slug).exclude(sku=data['sku']).exists():
        slug = f"{base_slug}-{idx}"
        idx += 1
    
    price = data['price']
    sale_price = None
    if data.get('old_price') and data['old_price'] > price:
        sale_price = price
        regular_price = data['old_price']
    else:
        regular_price = price
    
    product, created = Product.objects.update_or_create(
        sku=data['sku'],
        defaults={
            'name': data['name'],
            'slug': slug,
            'category': data['category'],
            'brand': data.get('brand'),
            'price': regular_price,
            'sale_price': sale_price,
            'stock': data.get('stock', 10),
            'short_description': data.get('short_description', ''),
            'description': data.get('description', ''),
            'specifications': {f"spec_{i}": f for i, f in enumerate(data.get('features', []))},
            'is_featured': data.get('is_featured', False),
            'is_new': True,
            'status': 'in_stock',
            'is_active': True,
        }
    )
    
    if image_sources:
        for i, src in enumerate(image_sources):
            dest_name = f"{data['sku'].lower()}_{i+1}.jpg"
            rel_path = copy_and_convert_image(src, dest_name)
            if rel_path:
                img_obj, img_created = ProductImage.objects.get_or_create(
                    product=product,
                    image=rel_path,
                    defaults={'is_primary': (i == 0), 'order': i, 'alt_text': product.name}
                )

    status_str = "CRÉÉ" if created else "MIS À JOUR"
    displayed_price = sale_price if sale_price else regular_price
    print(f"[{status_str}] {product.name} ({displayed_price:,} FCFA) - SKU: {product.sku}")
    return product

def run_import():
    print("=== DÉBUT IMPORTATION DU LOT 2 DE NOUVEAUX PRODUITS ===")
    
    # Catégories
    cat_meubles = get_or_create_cat("Meubles & Mobilier", icon="couch")
    cat_salon = get_or_create_cat("Le Salon & Séjour", parent_slug=cat_meubles.slug, icon="sofa")
    cat_sam = get_or_create_cat("Salle à Manger & Tables", parent_slug=cat_meubles.slug, icon="utensils")
    cat_refrig = Category.objects.filter(slug='refrigerateurs-congelateurs').first() or get_or_create_cat("Réfrigérateurs & Congélateurs", icon="refrigerator")
    cat_clim = Category.objects.filter(slug='climatisation').first() or get_or_create_cat("Climatisation & Ventilation", icon="fan")
    cat_cuisson = get_or_create_cat("Cuisinières & Cuisson", parent_slug=Category.objects.filter(slug='electromenager-cuisine').first().slug if Category.objects.filter(slug='electromenager-cuisine').exists() else None, icon="fire")
    cat_sport = get_or_create_cat("Sports, Vélos & Loisirs", icon="bicycle")

    # Marques
    b_onizuka = get_or_create_brand("Onizuka Confort")
    b_etoile = get_or_create_brand("Étoile")
    b_innova = get_or_create_brand("Innova")
    b_kaysun = get_or_create_brand("Kaysun")
    b_luta = get_or_create_brand("Luta")
    b_excellent = get_or_create_brand("Excellent")

    # 1. Cuisinière 6 feux mix gaz et courant (340 000 FCFA)
    create_product({
        "sku": "CUIS-6F-MIX-SACCI",
        "name": "Cuisinière Grande Largeur 6 Feux Mixte Gaz et Électrique Étoile Sacci Inox",
        "category": cat_cuisson,
        "brand": b_etoile,
        "price": 340000,
        "badge": "Grande Capacité 6 Feux",
        "is_featured": True,
        "short_description": "Cuisinière professionnelle 6 feux mixte (4 brûleurs gaz haute puissance + 2 plaques électriques en fonte). Grand four multifonction, couvercle en verre et finition inox premium.",
        "description": "La cuisinière idéale pour les passionnés de cuisine, grandes familles et réceptions à Bamako.\n\n- Table de cuisson 6 foyers polyvalente : 4 brûleurs à gaz rapides avec grilles émaillées robustes + 2 plaques électriques indépendantes pour cuisiner même en cas de rupture de gaz\n- Allumage automatique intégré aux manettes et sécurité thermocouple\n- Très grand four à double vitrage panoramique thermo-isolant\n- Tournebroche rotatif et grilloir électrique pour de délicieux rôtis\n- Couvercle de protection en verre trempé transparent\n- Finition corps inox et manettes ergonomiques.",
        "features": ["Table mixte 4 gaz + 2 plaques électriques", "Grand four multifonction avec tournebroche", "Allumage automatique et sécurité", "Finition inox brossé haute résistance", "Couvercle en verre trempé"],
    }, ["media_1795869995552_1915dec0.jpg"])

    # 2. Meuble TV avec support (32" à 55") Rolls-Royce (115 000 FCFA)
    create_product({
        "sku": "MEUBLE-TV-RR-115",
        "name": "Meuble TV avec Colonne Support Intégrée 32\" à 55\" Édition Gold RR",
        "category": cat_salon,
        "brand": b_onizuka,
        "price": 115000,
        "badge": "Support TV 32-55\" Inclus",
        "is_featured": True,
        "short_description": "Meuble TV contemporain noir & or avec support potence métallique universel pour écrans de 32 à 55 pouces (pas besoin de percer le mur !), tiroirs dorés gravés et étagères vitrées.",
        "description": "Une solution tout-en-un chic et ultra-pratique pour votre salon.\n\n- Potence métallique robuste intégrée supportant tous les téléviseurs de 32 à 55 pouces (standard VESA universel)\n- Plateau en verre trempé noir sérigraphié quadrillé de grand lustre\n- Façades de tiroirs en relief cannelé doré avec emblème de luxe\n- Niche centrale avec étagères en verre pour décodeurs, box TV et consoles de jeux\n- Piétement surélevé doré assurant une parfaite stabilité.",
        "features": ["Support écran 32\" à 55\" orientable intégré", "Évite de percer les murs", "Façades tiroirs dorées cannelées", "Plateau verre trempé résistant", "Rangement décodeur & accessoires"],
    }, ["media_1795870075569_e4448935.jpg"])

    # 3. VTT Vélo Luta Super-Boss TLJ003-26 (85 000 FCFA - 4 coloris)
    create_product({
        "sku": "VELO-LUTA-TLJ003-26",
        "name": "Vélo VTT 26 Pouces Tout-Terrain Luta Super-Boss TLJ003-26 (Multi-vitesses)",
        "category": cat_sport,
        "brand": b_luta,
        "price": 85000,
        "badge": "26 Pouces Tout-Terrain",
        "is_featured": True,
        "short_description": "Vélo VTT adulte tout-terrain 26 pouces Luta Super-Boss TLJ003-26. Cadre acier allégé haute résistance, freins à disque avant/arrière, transmission multi-vitesses, fourche télescopique suspendue. Disponible en plusieurs coloris éclatants.",
        "description": "Le vélo VTT Luta Super-Boss TLJ003-26 est parfait pour le sport, les balades et les déplacements urbains quotidiens à Bamako.\n\n- Roues 26 pouces avec pneus crantés tout-terrain à haute adhérence\n- Double freinage à disque mécanique avant et arrière pour un arrêt net et sécurisé par tous les temps\n- Fourche avant suspendue amortissant les chocs et nids-de-poule\n- Système de changement de vitesses fluide et précis pour monter les côtes sans effort\n- Selle ergonomique ajustable en hauteur avec attache rapide\n- Disponible en coloris : Gris Ardoise, Bleu Turquoise, Bleu Azur et Orange Sport.",
        "features": ["Taille roues 26 pouces", "Freins à disque avant et arrière", "Fourche télescopique amortisseur", "Transmission multi-vitesses", "Pneus tout-terrain renforcés"],
    }, ["media_1795870091213_92a3609e.jpg", "media_1795870095792_5a005284.jpg", "media_1795870104318_905737a3.jpg", "media_1795870114716_c26671dd.jpg"])

    # 4. Réfrigérateur combiné Innova 150L IN-255 (185 000 FCFA)
    create_product({
        "sku": "INNOVA-IN255-150L",
        "name": "Réfrigérateur Combiné Innova 150 Litres IN-255 Smart Sensor Inox",
        "category": cat_refrig,
        "brand": b_innova,
        "price": 185000,
        "badge": "Smart Sensor 150L",
        "is_featured": True,
        "short_description": "Réfrigérateur combiné 150 Litres Innova IN-255 finition inox brossé, congélateur bas à 3 compartiments tiroirs, régulation intelligente Smart Sensor et serrure.",
        "description": "Le combiné Innova IN-255 associe une esthétique moderne en inox et des performances de froid remarquables.\n\n- Capacité totale de 150 Litres\n- Technologie Innovated Defrost Tech avec Smart Sensor pour une température constante\n- Congélateur bas à 3 tiroirs transparents indépendants\n- Clayettes Crystal Glass Shelves en verre sécurit\n- Consommation énergétique optimisée Energy Saving (187 kWh/an)\n- Serrure de sécurité à clé intégrée.",
        "features": ["Capacité 150 Litres", "Congélateur bas 3 tiroirs", "Technologie Smart Sensor", "Clayettes verre trempé Crystal", "Serrure à clé"],
    }, ["media_1795869909374_9e290545.jpg", "media_1795869917534_afd9e654.jpg"])

    # 5. Cuisinière mixte Kaysun 4 feux (185 000 FCFA)
    create_product({
        "sku": "CUIS-KAYSUN-MIXTE-4F",
        "name": "Cuisinière Mixte 4 Feux Kaysun Noire (2 Feux Gaz + 2 Plaques Électriques)",
        "category": cat_cuisson,
        "brand": b_kaysun,
        "price": 185000,
        "badge": "Mixte 2 Gaz + 2 Élec",
        "is_featured": True,
        "short_description": "Cuisinière compacte 4 feux mixte Kaysun finition noir laqué (2 brûleurs à gaz + 2 plaques chauffantes électriques en fonte). Grand four avec porte double vitrage et couvercle en verre.",
        "description": "La cuisinière mixte Kaysun offre la polyvalence absolue pour votre cuisine : utilisez le gaz au quotidien et les plaques électriques en cas de bouteille de gaz vide !\n\n- 2 brûleurs à gaz rapides avec grille émaillée\n- 2 plaques électriques en fonte à chauffe constante\n- Four volumineux avec éclairage et grilloir\n- Finition carrosserie noire élégante et manettes chromées\n- Couvercle supérieur en verre trempé de protection.",
        "features": ["2 brûleurs gaz + 2 plaques électriques", "Four spacieux avec grilloir", "Finition noir laqué moderne", "Couvercle en verre trempé", "Pieds réglables"],
    }, ["media_1795870142007_429b4db0.jpg", "media_1795870148903_74bb4398.jpg"])

    # 6. Table à manger marbre 4 places contemporaine carrée (230 000 FCFA)
    create_product({
        "sku": "SAM-MARBRE-4P-CARREE-230",
        "name": "Ensemble Table à Manger 4 Places Marbre Gris Impérial & Fauteuils Cossus (230k)",
        "category": cat_sam,
        "brand": b_onizuka,
        "price": 230000,
        "badge": "Plateau Marbre Naturel",
        "is_featured": True,
        "short_description": "Table carrée 4 places haut de gamme avec plateau en marbre gris veiné blanc et 4 fauteuils ergonomiques enveloppants en cuir noir avec piétement fuselé. Livraison et montage inclus.",
        "description": "Une table à manger au chic contemporain irrésistible.\nSon plateau carré en marbre poli satiné offre un toucher frais et une résistance exceptionnelle aux rayures.\nLes 4 fauteuils assortis avec dossier enveloppant en demi-lune procurent un confort d'assise incomparable.\n\nLivraison et installation offertes à Bamako.",
        "features": ["Plateau en véritable marbre poli", "4 fauteuils grand confort en cuir noir", "Piétement lourd et stable", "Livraison et pose offertes"],
    }, ["media_1795869876476_949def0f.jpg"])

    # 7. Réfrigérateur Étoile combiné 50x50 Turquie XRD-220 (130 000 FCFA)
    create_product({
        "sku": "ETOILE-50X50-TURQUIE-130",
        "name": "Réfrigérateur Combiné 50x50 Étoile Nature Fresh Spécial Turquie XRD-220",
        "category": cat_refrig,
        "brand": b_etoile,
        "price": 130000,
        "badge": "Import Turquie 50x50",
        "is_featured": True,
        "short_description": "Réfrigérateur combiné compact format 50x50 cm Étoile fabriqué en Turquie. Congélateur bas à 3 tiroirs coulissants indépendants, régulateur de tension intégré et classe A+.",
        "description": "Conçu avec les standards de qualité turcs, le réfrigérateur Étoile 50x50 combine robustesse et compacité parfaite.\n\n- Dimensions idéales 50 cm x 50 cm pour les cuisines et espaces optimisés\n- Congélateur inférieur à 3 tiroirs coulissants avec poignées métalliques\n- Réfrigérateur haut avec clayettes en verre trempé et bac à légumes\n- Régulateur de tension protecteur intégré\n- Consommation économique certifiée A+.",
        "features": ["Format compact 50 x 50 cm", "Congélateur bas 3 tiroirs coulissants", "Régulateur de tension intégré", "Qualité certifiée Turquie", "Serrure à clé"],
    }, ["media_1795869737843_56ca6110.jpg", "media_1795869743660_5072ef0d.jpg"])

    # 8. Ventilateur à eau brumisateur géant 30 pouces Excellent (125 000 FCFA)
    create_product({
        "sku": "VENTILO-EAU-BRUMISATEUR-30",
        "name": "Ventilateur Brumisateur Géant à Eau 30 Pouces Excellent Industriel sur Roulettes",
        "category": cat_clim,
        "brand": b_excellent,
        "price": 125000,
        "badge": "Brumisateur Géant 30\"",
        "is_featured": True,
        "short_description": "Ventilateur brumisateur professionnel 30 pouces (75 cm) avec réservoir d'eau haute capacité sur roulettes. Baisse la température ambiante de 4 à 8°C grâce à sa brume ultrafine. Idéal pour cours, salons, terrasses et restaurants.",
        "description": "Dites adieu à la chaleur étouffante avec le ventilateur brumisateur à eau 30 pouces Excellent.\n\n- Diamètre géant de 30 pouces avec pales profilées en aluminium pour un brassage d'air surpuissant\n- Système de brumisation centrifuge à micro-gouttelettes rafraîchissant l'air instantanément sans mouiller\n- Bac réservoir d'eau indépendant de grande contenance (plusieurs heures d'autonomie continue)\n- Châssis métallique lourd monté sur 4 roulettes orientables avec freins\n- Vitesse réglable, oscillation grand angle et débit de brume ajustable.",
        "features": ["Diamètre 30 pouces (75 cm)", "Baisse réelle de la température de 4 à 8°C", "Réservoir d'eau grande autonomie", "Monté sur roulettes mobiles", "Idéal terrasse, salon, cour et commerce"],
    }, ["media_1795869772926_66064f01.jpg"])

    # 9. Table basse gigogne ronde 2 pièces avec tiroir cannelé (95 000 FCFA - 3 modèles)
    create_product({
        "sku": "TB-RONDE-2P-TIROIR-95",
        "name": "Ensemble Table Basse Gigogne Ronde 2 Pièces avec Tiroir Cannelé & Marbre (95k)",
        "category": cat_salon,
        "brand": b_onizuka,
        "price": 95000,
        "badge": "Tiroir Rangement Intégré",
        "is_featured": True,
        "short_description": "Table basse double ronde gigogne avec plateau marbre noble, structure métal doré ou blanc et grand tiroir de rangement cylindrique à relief plissé avec poignée bijou dorée.",
        "description": "L'ensemble table basse gigogne ronde 2 pièces allie élégance scandinave et praticité moderne.\n\n- Grande table haute avec plateau en verre trempé effet marbre\n- Petite table basse encastrable munie d'un tiroir circulaire spacieux à façade plissée cannelée\n- Disponible en plusieurs déclinaisons : Marbre blanc & piétement doré, Marbre noir & or, ou Tout blanc laqué\n- Idéale pour ranger télécommandes, revues et créer une composition modulable dans le salon.",
        "features": ["Ensemble de 2 tables rondes gigognes", "Tiroir de rangement circulaire intégré", "Plateau marbre haute brillance", "Structure métal doré ou laqué"],
    }, ["media_1795869807149_a5f5817a.jpg", "media_1795869814042_949d41b6.jpg", "media_1795869823471_57de1162.jpg"])

    # 10. Salle à manger 4 places luxe Chanel / Noyer verre trempé (260 000 FCFA - 2 finitions)
    create_product({
        "sku": "SAM-LUXE-4P-260",
        "name": "Ensemble Salle à Manger 4 Places Haute Couture Luxe (260k)",
        "category": cat_sam,
        "brand": b_onizuka,
        "price": 260000,
        "badge": "Luxe Haute Couture",
        "is_featured": True,
        "short_description": "Table de salle à manger 4 places prestige avec plateau en verre trempé biseauté (Finition Noir & Or Haute Couture ou Finition Noyer Boisé Laqué) et 4 fauteuils capitonnés en cuir taupe avec pieds dorés. Installation gratuite.",
        "description": "Le raffinement suprême pour votre salle à manger avec cet ensemble 4 places d'inspiration haute couture.\n\n- Plateau en verre trempé épais haute résistance bordé d'une frise dorée élégante ou finition noyer glacé\n- 4 fauteuils cossus au dossier galbé en cuir texturé taupe avec pieds métalliques fuselés et embouts en laiton doré\n- Une tenue de table majestueuse qui sublime immédiatement votre intérieur.\n\nLivraison et installation offertes à Bamako.",
        "features": ["Plateau verre trempé biseauté haute brillance", "4 fauteuils de luxe en cuir avec pieds laiton doré", "Finitions raffinées Haute Couture", "Montage offert à Bamako"],
    }, ["media_1795869846754_6f829519.jpg", "media_1795869859981_5cee6552.jpg"])

    # 11. Table basse gigogne carrée 3 pièces métal doré & marbre/verre (74 000 FCFA - 3 finitions)
    create_product({
        "sku": "TB-GIGOGNE-CARREE-3P-74",
        "name": "Ensemble Table Basse Gigogne Carrée 3 Pièces Métal Doré Prestige (74k)",
        "category": cat_salon,
        "brand": b_onizuka,
        "price": 74000,
        "badge": "Set de 3 Tables Gigognes",
        "is_featured": True,
        "short_description": "Trio de tables basses gigognes carrées superposables en acier doré miroir brillant avec plateaux marbre blanc, marbre noir ou verre trempé noir. Pieds géométriques en cercles.",
        "description": "Un ensemble ingénieux et très décoratif composé de 3 tables gigognes carrées de hauteurs graduées.\n\n- Se glissent les unes sous les autres pour libérer l'espace ou se déploient lors de vos réceptions\n- Châssis en acier doré poli miroir avec traverses décoratives en anneaux dorés\n- Plateaux résistants disponibles en Marbre blanc veiné, Marbre noir intense ou Verre noir laqué\n- Apportent une touche lumineuse et prestigieuse à tout salon.",
        "features": ["Lot complet de 3 tables gigognes", "Gain de place optimal", "Structure en acier doré brillant", "Plateaux marbre / verre trempé"],
    }, ["media_1795870169495_37538797.jpg", "media_1795870174925_6adaea2e.jpg", "media_1795870183717_59b828bd.jpg", "media_1795870190819_d63b6cef.jpg"])

    # 12. Table basse gigogne ronde 2 pièces bois noyer (59 000 FCFA)
    create_product({
        "sku": "TB-RONDE-BOIS-NOYER-59",
        "name": "Ensemble Table Basse Gigogne Ronde 2 Pièces Bois Noyer Chaleureux (59k)",
        "category": cat_salon,
        "brand": b_onizuka,
        "price": 59000,
        "badge": "Bois Noyer Scandinave",
        "is_featured": True,
        "short_description": "Duo de tables basses gigognes rondes avec plateaux en bois noyer naturel à bords rebord anti-chute et piètement en métal noir géométrique.",
        "description": "Le charme naturel et intemporel du bois noyer dans votre salon.\n\n- Deux tables rondes de diamètres complémentaires (haute et basse encastrable)\n- Plateaux bois avec rebord profilé élégant empêchant les objets et verres de glisser\n- Structure métallique noire croisée assurant une excellente stabilité\n- Idéale pour les petits et moyens salons.",
        "features": ["Lot de 2 tables gigognes", "Plateau bois finition noyer naturel", "Rebord profilé anti-chute", "Piètement métal noir robuste"],
    }, ["media_1795870206658_c0ef7738.jpg"])

    # 13. Meuble TV avec support étirable prolongeable marbre crème (135 000 FCFA)
    create_product({
        "sku": "MEUBLE-TV-EXTENSIBLE-135",
        "name": "Meuble TV Extensible & Prolongeable avec Support TV Intégré Marbre Crème (135k)",
        "category": cat_salon,
        "brand": b_onizuka,
        "price": 135000,
        "badge": "Extensible & Support Inclus",
        "is_featured": True,
        "short_description": "Meuble TV moderne extensible en longueur selon la taille de votre salon, équipé d'une potence support TV intégrée pour écrans plats, plateau marbre crème et tiroirs sculptés.",
        "description": "Le meuble TV adaptatif par excellence !\n\n- Système coulissant extensible permettant d'ajuster la longueur du meuble selon l'espace disponible de votre pièce\n- Colonne support TV centrale intégrée évitant tout perçage mural\n- Plateau supérieur façon marbre blanc-crème veiné\n- 4 grands compartiments tiroirs avec poignées et motifs en relief pour ranger tous vos appareils et câbles.",
        "features": ["Longueur extensible et modulable", "Support TV universel intégré", "Plateau décor marbre crème", "Nombreux tiroirs de rangement"],
    }, ["media_1795870222933_8d6f9f72.jpg"])

    # 14. Ensemble Meuble TV + Table basse complet luxe marbre (375 000 FCFA - 3 modèles : A3, A7, A9)
    ensembles_375k = [
        {
            "sku": "SET-TV-TB-375-A3",
            "name": "Ensemble Meuble TV Extensible + Table Basse Luxe Modèle A3 (375k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 375000,
            "badge": "Pack Complet TV + Table",
            "is_featured": True,
            "short_description": "Ensemble assorti meuble TV extensible et table basse design contemporain gris taupe et noyer avec arrondis profilés, tiroirs amortis et plateaux satinés. Montage offert.",
            "description": "L'ensemble Modèle A3 confère une harmonie design haut de gamme à votre salon.\nComprend le meuble TV extensible avec bloc d'angle arrondi et la table basse coordonnée avec compartiment de rangement intégré.\nLivraison et installation gratuites à Bamako.",
            "features": ["Meuble TV extensible + Table basse assortie", "Finition gris taupe et bois noyer", "Angles arrondis sécurisants", "Livraison & pose offertes à Bamako"],
            "images": ["media_1795870264301_d61e9b90.jpg"]
        },
        {
            "sku": "SET-TV-TB-375-A7",
            "name": "Ensemble Meuble TV Extensible + Table Basse Terrazzo Blanc & Verre Modèle A7 (375k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 375000,
            "badge": "Pack Complet TV + Table",
            "is_featured": True,
            "short_description": "Ensemble meuble TV et table basse étirable avec plateau terrazzo minéral blanc moucheté, tablette en verre fumé et caisson laqué crème.",
            "description": "L'ensemble Modèle A7 se démarque par son plateau original en terrazzo blanc lumineux et sa console pivotante en verre fumé.\nUn must du design avant-gardiste pour sublimer les grands salons.",
            "features": ["Plateau terrazzo minéral et verre fumé", "Meuble TV étirable multi-niveaux", "Table basse assortie", "Installation incluse"],
            "images": ["media_1795870271408_44560a2c.jpg"]
        },
        {
            "sku": "SET-TV-TB-375-A9",
            "name": "Ensemble Meuble TV + Table Basse Marbre Noir Marquina Modèle A9 (375k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 375000,
            "badge": "Pack Complet TV + Table",
            "is_featured": True,
            "short_description": "Ensemble meuble TV et table basse en marbre noir intense veiné blanc, caisson noir graphite mat et petite table d'appoint latérale noyer intégrée.",
            "description": "L'ensemble Modèle A9 incarne l'élégance obscure et luxueuse du marbre noir Marquina.\nLes lignes épurées et les finitions feutrées créent un salon d'architecte d'une beauté saisissante.",
            "features": ["Plateau marbre noir Marquina", "Table basse avec desserte bois intégrée", "Meuble TV spacieux", "Montage offert à Bamako"],
            "images": ["media_1795870278473_b596c3ef.jpg"]
        }
    ]
    for e in ensembles_375k:
        create_product(e, e['images'])

    # 15. Ensemble Meuble TV + Table basse complet marbre (190 000 FCFA - 4 déclinaisons)
    ensembles_190k = [
        {
            "sku": "SET-TV-TB-190-AMBRE",
            "name": "Ensemble Meuble TV + Table Basse Plateau Marbre Ambré & Façades Dorées (190k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 190000,
            "badge": "Pack Salon Marbre & Or",
            "is_featured": True,
            "short_description": "Ensemble salon complet comprenant le meuble TV avec plateau marbre ambre chaleureux et la table basse assortie à tiroirs dorés cannelés.",
            "description": "Cet ensemble complet meuble TV + table basse offre un rapport qualité/prix exceptionnel à 190 000 FCFA.\nPlateaux en verre trempé finition marbre précieux et façades de tiroirs en relief doré avec poignées bouton bijou.",
            "features": ["Pack 2 pièces : Meuble TV + Table basse", "Plateau marbre ambré haute brillance", "Tiroirs de rangement fonctionnels"],
            "images": ["media_1795870305544_c1e08cac.jpg"]
        },
        {
            "sku": "SET-TV-TB-190-BLANC-NOYER",
            "name": "Ensemble Meuble TV + Table Basse Marbre Blanc & Noyer Doré (190k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 190000,
            "badge": "Pack Salon Blanc & Noyer",
            "short_description": "Ensemble meuble TV et table basse plateau marbre blanc de Carrare, caisson noyer foncé et tiroirs blanc plissé avec miroirs bronze.",
            "description": "L'alliance parfaite de la lumière du marbre blanc et de la profondeur du noyer foncé pour un salon éclatant et chaleureux.",
            "features": ["Meuble TV + Table basse", "Plateau marbre blanc veiné", "Tiroirs biseautés"],
            "images": ["media_1795870311253_b1cc6768.jpg"]
        },
        {
            "sku": "SET-TV-TB-190-BLANC-OR-BAGUETTE",
            "name": "Ensemble Meuble TV + Table Basse Marbre Blanc & Baguettes d'Or (190k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 190000,
            "badge": "Pack Salon Blanc & Or",
            "short_description": "Ensemble meuble TV et table basse plateau marbre blanc et façades tiroirs blanches laquées sublimées par des cartouches ovales dorés.",
            "description": "Un design géométrique très chic avec cartouches dorés sur les tiroirs et plateau marbre blanc lumineux.",
            "features": ["Meuble TV + Table basse", "Cartouches ovales dorés", "Plateau marbre blanc"],
            "images": ["media_1795870316624_8c1b3319.jpg"]
        },
        {
            "sku": "SET-TV-TB-190-MARBRE-NOIR",
            "name": "Ensemble Meuble TV + Table Basse Marbre Noir & Blanc Contrasté (190k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 190000,
            "badge": "Pack Salon Noir & Blanc",
            "short_description": "Ensemble meuble TV et table basse plateau marbre noir marbré blanc éclatant, caisson noir et tiroirs blanc laqué strié.",
            "description": "Un contraste saisissant et moderne qui donne immédiatement du caractère à votre salon.",
            "features": ["Meuble TV + Table basse", "Marbre noir veiné blanc de prestige", "Tiroirs de rangement"],
            "images": ["media_1795870326550_4541e87e.jpg"]
        }
    ]
    for e in ensembles_190k:
        create_product(e, e['images'])

    # 16. Ensemble Table complet luxe marbre pivotant / galbé (400 000 FCFA - 3 modèles : M31, M38, M56-150#)
    ensembles_400k = [
        {
            "sku": "SET-TV-TB-400-M31",
            "name": "Ensemble Meuble TV Galbé + Table Basse Ovale Pivotante Marbre Modèle M31 (400k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 400000,
            "badge": "Grand Luxe Pivotant M31",
            "is_featured": True,
            "short_description": "Ensemble d'exception salon contemporain avec meuble TV galbé aux extrémités arrondies et table basse ovale pivotante à double plateau marbre blanc et tiroirs coulissants. Installation offerte.",
            "description": "Le Modèle M31 représente le nec plus ultra du mobilier de salon moderne.\nLa table basse ovale dispose d'un plateau supérieur en marbre qui pivote pour agrandir la surface selon vos réceptions.\nLe meuble TV assorti étirable offre des courbes galbées fluides et des tiroirs grande capacité.\nLivraison et montage inclus à Bamako.",
            "features": ["Table basse ovale à plateau pivotant", "Meuble TV galbé contemporain", "Plateau marbre blanc noble", "Montage et installation offerts"],
            "images": ["media_1795870343406_4fccef3e.jpg"]
        },
        {
            "sku": "SET-TV-TB-400-M38",
            "name": "Ensemble Meuble TV Architectural + Table Basse Verre Fumé & Bois Modèle M38 (400k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 400000,
            "badge": "Grand Luxe Design M38",
            "is_featured": True,
            "short_description": "Ensemble meuble TV à piétement en X architectural et table basse ovale à double plateau en verre fumé trempé et bois anthracite avec fermeture zippée dorée.",
            "description": "Le Modèle M38 séduit les amateurs d'architecture contemporaine avec son meuble TV suspendu sur croisillons métalliques et sa table basse ovale bi-matière.",
            "features": ["Design architectural sur piétement X", "Double plateau verre fumé et bois texturé", "Finition gris graphite & dorures"],
            "images": ["media_1795870349541_dea4b889.jpg"]
        },
        {
            "sku": "SET-TV-TB-400-M56-150",
            "name": "Ensemble Meuble TV Haricot Galbé + Table Basse Galet Marbre Modèle M56-150# (400k)",
            "category": cat_salon,
            "brand": b_onizuka,
            "price": 400000,
            "badge": "Formes Organiques Galet",
            "is_featured": True,
            "short_description": "Ensemble ultra-organique forme galet/haricot en blanc crème laqué et bois chaleureux avec plateau marbre poli et tiroirs invisibles amortis.",
            "description": "La grande tendance des formes douces et organiques avec le Modèle M56-150#.\nLes courbes harmonieuses de la table galet et du meuble TV apportent une sérénité et une douceur visuelle incomparable à votre intérieur.",
            "features": ["Formes organiques galet & haricot", "Plateau marbre blanc doux", "Tiroirs amortis avec poignées dorées", "Livraison et montage inclus à Bamako"],
            "images": ["media_1795870357234_7951d675.jpg"]
        }
    ]
    for e in ensembles_400k:
        create_product(e, e['images'])

    print("\n🎉 === IMPORTATION DU LOT 2 TERMINÉE AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    run_import()
