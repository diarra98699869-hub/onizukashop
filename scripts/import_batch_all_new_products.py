"""
Script d'importation complète et propre du nouveau lot de produits :
1. Chambres à coucher 599k (4 modèles : 8805#, 8812#, 8806#, 802#)
2. Machine à café à capsules Nespresso Inissia De'Longhi (70k promo au lieu de 90k)
3. Réfrigérateur East Point 400L (290k)
4. Réfrigérateur East Point 250L (190k)
5. Chambres à coucher 649k au lieu de 700k avec veilleuse LED digitale (5 modèles : MLK-602#, 6650#, 923#, 8807#, 922#)
6. Réfrigérateur Étoile XRD-140 combiné 140L (180k)
7. Réfrigérateur Étoile XRD-128 combiné 128L (139k)
8. Réfrigérateur Bar Étoile XRD-100 2 portes 100L (90k)
9. Réfrigérateur Bar Étoile XR-100 1 porte 100L (79k)
10. Sonifer Plaque à infrarouge 1 feux SF-3043 (38k)
11. Coiffeuses simples avec lumière LED digitale (122k - 2 modèles : 903#, 896#)
12. Salles à manger 4 places surface en vitre (105k - 3 modèles/designs)
13. Salles à manger 4 places surface en bois (120k - 6 modèles/finitions distincts)
14. Samsung TV 85" Mini-LED M70HD 2026 (1 025 000 FCFA)
15. Samsung TV 75" Mini-LED M70HD 2026 (790 000 FCFA)
16. Chambres à coucher 3 places avec veilleuse LED digitale 670k (5 modèles : 9056#, 110#, 9047#, KD-316#, MC2203#)
17. Matelas grand confort (Épaisseur 20 avec fer = 138k, Épaisseur 25 avec fer = 152k, Épaisseur 25 sans fer = 172k)
18. Chambres à coucher 3 places avec veilleuse LED digitale 700k (5 modèles : MC2203# beige/doré, KD-309#, KD-304#, MC615#, HN-507#, HN-502#, KD-303#, KD-312#, KD-307#)
19. Moustiquaire électrique Winning Star ST-4037 3000V (26k)
20. Enceintes Boom Okop & Winning Star :
    - Okop KP-8013 (135 000 FCFA)
    - Okop KP-8010 (99 000 FCFA)
    - Okop KP-8011 (69 000 FCFA)
    - Boom 8006 (72 000 FCFA)
    - Boom 8004 (42 000 FCFA)
    - Boom 8007 (80 000 FCFA)
    - Winning Star ST-8101 Party Box (85 000 FCFA)
21. Sonifer Plaque à infrarouge 2 feux SF-3051 (68k)
22. Chauffe-eau douche Milano (30L = 77 000 FCFA, 50L = 87 500 FCFA)
23. Salle à manger luxe marbre 6 places (360 000 FCFA)
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
    dest_path = MEDIA_PRODUCTS / dest_filename
    if dest_path.exists():
        # L'image existe déjà dans media/products (ex: issue du repo Git ou d'un import précédent)
        return f"products/{dest_filename}"

    src_path = USER_UPLOADED_DIR / src_name
    if src_path.exists():
        try:
            with Image.open(src_path) as img:
                # Convert to RGB (in case of RGBA/P)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=90, optimize=True)
            return f"products/{dest_filename}"
        except Exception as e:
            print(f"Erreur conversion {src_name}: {e}")
            shutil.copy2(src_path, dest_path)
            return f"products/{dest_filename}"
    else:
        print(f"Fichier image introuvable dans uploads ({src_path}) et media ({dest_path})")
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
    # Si old_price est défini, c'est que price est le prix promo
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
    
    # Gestion des images
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
    print("=== DÉBUT IMPORTATION DU NOUVEAU CATALOGUE ===")
    
    # 1. Catégories & Marques nécessaires
    cat_meubles = get_or_create_cat("Meubles & Mobilier", icon="couch")
    cat_chambre = get_or_create_cat("Chambre à Coucher", parent_slug=cat_meubles.slug, icon="bed")
    cat_salon = get_or_create_cat("Le Salon & Séjour", parent_slug=cat_meubles.slug, icon="sofa")
    cat_salle_manger = get_or_create_cat("Salle à Manger & Tables", parent_slug=cat_meubles.slug, icon="utensils")
    cat_matelas = get_or_create_cat("Matelas & Literie", parent_slug=cat_meubles.slug, icon="bed")
    
    cat_refrig = Category.objects.filter(slug='refrigerateurs-congelateurs').first() or get_or_create_cat("Réfrigérateurs & Congélateurs", icon="refrigerator")
    cat_tv = Category.objects.filter(slug='televiseurs').first() or get_or_create_cat("Téléviseurs & Smart TV", icon="tv")
    
    cat_electromenager = get_or_create_cat("Électroménager & Cuisine", icon="blender")
    cat_audio = get_or_create_cat("Audio & Enceintes Bluetooth", icon="volume-high")
    cat_sanitaire = get_or_create_cat("Sanitaire & Chauffe-Eau", icon="shower")
    cat_maison = get_or_create_cat("Maison & Protection", icon="shield")

    # Marques
    b_onizuka = get_or_create_brand("Onizuka Confort")
    b_samsung = get_or_create_brand("Samsung")
    b_nespresso = get_or_create_brand("Nespresso")
    b_eastpoint = get_or_create_brand("East Point")
    b_etoile = get_or_create_brand("Étoile")
    b_sonifer = get_or_create_brand("Sonifer")
    b_milano = get_or_create_brand("Milano")
    b_okop = get_or_create_brand("Okop")
    b_winning_star = get_or_create_brand("Winning Star")

    # ==========================================
    # LOT 1 : 4 Chambres à Coucher (599 000 FCFA promo / 650 000 FCFA)
    # Livraison & installation gratuite à Bamako
    # ==========================================
    bedrooms_599k = [
        {
            "sku": "CHAMBRE-8805",
            "name": "Ensemble Chambre à Coucher Complète Grand Luxe Modèle 8805#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 599000,
            "old_price": 650000,
            "is_promo": True,
            "badge": "Promo -51 000 F",
            "is_featured": True,
            "short_description": "Ensemble chambre moderne complet avec lit King Size capitonné, armoire 4 portes avec miroirs & motifs géométriques, coiffeuse et 2 tables de chevet. Livraison et installation incluses à Bamako.",
            "description": "Sublimez votre suite parentale avec l'ensemble chambre à coucher complète Modèle 8805#. Cet ensemble haut de gamme allie l'élégance du bois noble et finitions gris anthracite avec des détails géométriques contemporains.\n\nContenu du pack :\n- 1x Grand Lit King Size avec tête de lit capitonnée velours beige et inserts géométriques\n- 1x Armoire majestueuse 4 portes avec grands miroirs biseautés et penderies spacieuses\n- 1x Coiffeuse moderne avec grand miroir et tiroirs coulissants\n- 2x Tables de chevet coordonnées avec tiroirs\n\nService VIP Onizuka Shop : Livraison et installation complètes offertes à votre domicile à Bamako par nos techniciens menuisiers professionnels.",
            "features": ["Lit King Size 3 places", "Armoire 4 portes avec miroirs", "Coiffeuse avec grand miroir", "2 tables de chevet intégrées", "Livraison & Installation incluses à Bamako"],
            "images": ["media_1795868488620_45135195.jpg"]
        },
        {
            "sku": "CHAMBRE-8812",
            "name": "Ensemble Chambre à Coucher Complète Moderne Modèle 8812#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 599000,
            "old_price": 650000,
            "is_promo": True,
            "badge": "Promo -51 000 F",
            "is_featured": True,
            "short_description": "Ensemble de chambre ultra-design finition gris graphite & noyer, motifs losanges luxueux, tête de lit capitonnée ergonomique. Installation offerte.",
            "description": "L'ensemble chambre à coucher Modèle 8812# offre une esthétique raffinée avec ses motifs géométriques en résille dorée et son alliance de noyer chaud et de gris foncé laqué.\n\nContenu :\n- Lit 3 places grand confort avec dosseret capitonné alvéolé\n- Grande armoire 4 portes avec portes miroirs centrales\n- Commode / Coiffeuse multifonction avec miroir assorti\n- 2 tables de nuit modernes\n\nInclus : Livraison sécurisée et montage professionnel gratuit à Bamako.",
            "features": ["Design contemporain noyer & graphite", "Motifs dorés géométriques", "Armoire 4 portes grande capacité", "Livraison & Pose gratuites à Bamako"],
            "images": ["media_1795868495338_3d36e362.jpg"]
        },
        {
            "sku": "CHAMBRE-8806",
            "name": "Ensemble Chambre à Coucher Complète Boisée Prestige Modèle 8806#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 599000,
            "old_price": 650000,
            "is_promo": True,
            "badge": "Promo -51 000 F",
            "is_featured": True,
            "short_description": "Design royal bois naturel & gris ardoise rehaussé de claustras dorés élégants. Lit King Size, armoire 4 portes, commode coiffeuse. Montage inclus.",
            "description": "Le Modèle 8806# séduit par sa chaleur naturelle et ses détails architecturaux dorés inspirés des intérieurs de prestige.\n\nLe pack comprend le grand lit, l'armoire dressing 4 portes avec miroirs, la coiffeuse stylisée et 2 tables de nuit.\nLivraison et installation soignée sans supplément partout à Bamako.",
            "features": ["Finitions boisées nobles et gris ardoise", "Détails claustra dorés", "Lit King Size avec chevet capitonné", "Livraison et installation clé en main"],
            "images": ["media_1795868502424_2341b719.jpg"]
        },
        {
            "sku": "CHAMBRE-802",
            "name": "Ensemble Chambre à Coucher Complète Crème & Or Modèle 802#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 599000,
            "old_price": 650000,
            "is_promo": True,
            "badge": "Promo -51 000 F",
            "is_featured": True,
            "short_description": "Ensemble lumineux crème nacré et inserts losanges dorés. Tête de lit capitonnée rose poudré/beige, armoire 4 portes. Pose offerte.",
            "description": "Illuminez votre chambre avec le Modèle 802# en ton crème laqué rehaussé d'élégants motifs diamants dorés.\n\nComposé du lit avec tête de lit capitonnée de luxe, d'une grande armoire dressing 4 portes, d'une coiffeuse spacieuse et de deux chevets coordonnés.\nBénéficiez du service d'installation gratuite directement dans votre chambre à Bamako.",
            "features": ["Finition laquée crème nacrée", "Inserts losanges dorés prestige", "Capitonnage confort haut de gamme", "Livraison & Installation offertes"],
            "images": ["media_1795868509614_7d9fca21.jpg"]
        }
    ]
    for b in bedrooms_599k:
        create_product(b, b['images'])

    # ==========================================
    # 2. Machine à café Nespresso Inissia De'Longhi (70 000 FCFA promo / 90 000 FCFA)
    # ==========================================
    create_product({
        "sku": "NESP-INISSIA-EN80B",
        "name": "Machine à Café à Capsules Nespresso Inissia De'Longhi EN80.B",
        "category": cat_electromenager,
        "brand": b_nespresso,
        "price": 70000,
        "old_price": 90000,
        "is_promo": True,
        "badge": "Offre Flash -20 000 F",
        "is_featured": True,
        "short_description": "Machine à café compacte Nespresso Inissia par De'Longhi (Type EN80.B). Pression 19 bars, chauffe ultra-rapide 25s, 2 longueurs de tasse programmables (Espresso & Lungo).",
        "description": "Dégustez un véritable espresso italien crémeux à la maison ou au bureau avec la machine Nespresso Inissia originale par De'Longhi (Modèle EN80.B Noir).\n\n- Pression professionnelle 19 bars pour une mousse crémeuse parfaite\n- Système de chauffe Thermobloc rapide (prête en 25 secondes)\n- 2 sélections automatiques : Espresso (40 ml) et Lungo (110 ml)\n- Format ultra-compact (12 x 23 x 32.1 cm) idéal pour toutes les cuisines et bureaux\n- Réservoir d'eau amovible 0.7 L et bac de récupération pour 11 capsules usagées\n- Arrêt automatique éco-énergétique après 9 minutes d'inactivité\n- Produit original scellé en boîte d'origine.",
        "features": ["Pression 19 bars", "Chauffe en 25 secondes", "Boutons Espresso & Lungo programmables", "Dimensions compactes 12 x 23 x 32 cm", "Garantie officielle Onizuka"],
    }, ["media_1795868445983_6e288ee1.jpg", "media_1795868451217_8beb9ec8.jpg", "media_1795868456638_e7933b3f.jpg"])

    # ==========================================
    # 3. Réfrigérateur East Point 400 Litres (290 000 FCFA)
    # ==========================================
    create_product({
        "sku": "EP-400L-REF",
        "name": "Réfrigérateur Double Porte East Point 400 Litres Tropicalisé EP-400L",
        "category": cat_refrig,
        "brand": b_eastpoint,
        "price": 290000,
        "is_featured": True,
        "badge": "Tropicalisé +45°C",
        "short_description": "Réfrigérateur double porte East Point 400L finition inox brossé premium, classe climatique Tropicalisée +45°C pour les fortes chaleurs de Bamako.",
        "description": "Le réfrigérateur East Point EP-400L est spécialement conçu pour garantir une fraîcheur optimale même par temps de grande chaleur sahélienne.\n\n- Capacité brute totale de 400 Litres avec compartiment congélateur supérieur généreux\n- Technologie Tropicalisée résistante jusqu'à +45°C de température ambiante\n- Clayettes modulables en verre trempé renforcé et balconnets de porte spacieux\n- Bac à légumes Fresh Zone à humidité contrôlée\n- Compresseur silencieux, faible consommation d'énergie (Low Noise & Energy Saving)\n- Finition inox silver moderne anti-traces.",
        "features": ["Capacité totale 400 Litres", "Double porte avec congélateur haut", "Classe Tropicalisée +45°C", "Compresseur éco-énergétique silencieux", "Clayettes verre trempé et bac fraîcheur"],
    }, ["media_1795868419894_46af8476.jpg", "media_1795868426958_10c6fd41.jpg"])

    # ==========================================
    # 4. Réfrigérateur East Point 250 Litres (190 000 FCFA)
    # ==========================================
    create_product({
        "sku": "EP-250L-REF",
        "name": "Réfrigérateur Double Porte East Point 250 Litres Tropicalisé EP-250L",
        "category": cat_refrig,
        "brand": b_eastpoint,
        "price": 190000,
        "badge": "Tropicalisé +45°C",
        "short_description": "Réfrigérateur double porte compact 250 Litres East Point inox silver, compresseur tropicalisé résistant +45°C.",
        "description": "Idéal pour les appartements, familles et bureaux, le réfrigérateur East Point EP-250L combine compacité et volume de stockage performant.\n\n- Volume utile de 250 Litres avec congélateur indépendant\n- Certifié Tropicalisé +45°C TROPIC pour un froid constant à Bamako\n- Étagères en verre trempé réglables en hauteur\n- Bac à fruits et légumes transparent et balconnets pour bouteilles\n- Consommation économique et fonctionnement très silencieux.",
        "features": ["Capacité 250 Litres", "Double porte froid séparé", "Tropicalisé +45°C", "Finitions inox élégantes", "Très faible niveau sonore"],
    }, ["media_1795868379825_13b1a910.jpg", "media_1795868386378_f65e2632.jpg"])

    # ==========================================
    # 5. Chambres à Coucher 3 places avec veilleuse lumineuse digitale (649 000 FCFA promo / 700 000 FCFA)
    # 5 modèles : MLK-602#, 6650#, 923#, 8807#, 922#
    # ==========================================
    bedrooms_649k = [
        {
            "sku": "CHAMBRE-LED-MLK602",
            "name": "Chambre à Coucher Complète 3 Places avec Veilleuse Digitale LED Modèle MLK-602#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 649000,
            "old_price": 700000,
            "is_promo": True,
            "badge": "Veilleuse LED Digitale",
            "is_featured": True,
            "short_description": "Chambre de luxe 3 places avec tête de lit capitonnée rétroéclairée LED tactile, armoire 4 portes coulissantes/battantes miroirs, commode coiffeuse avec miroir LED. Installation gratuite.",
            "description": "L'ensemble chambre complète Modèle MLK-602# intègre une technologie d'éclairage d'ambiance LED numérique haut de gamme.\n\nContenu :\n- Lit 3 places grand format avec tête de lit capitonnée et veilleuse LED intégrée à commande tactile\n- Armoire majestueuse avec grands miroirs biseautés et finitions blanc laqué & bois noyer\n- Coiffeuse design avec miroir cerclé de LED lumineuse et tiroirs spacieux\n- 2 tables de nuit coordonnées\n\nLivraison et installation complètes offertes à Bamako.",
            "features": ["Veilleuse LED digitale intégrée", "Lit 3 places grand luxe", "Armoire dressing 4 portes avec miroirs", "Coiffeuse avec miroir LED", "Montage et livraison inclus"],
            "images": ["media_1795868526140_44f95035.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-6650",
            "name": "Chambre à Coucher Complète 3 Places Veilleuse Lumineuse Modèle 6650#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 649000,
            "old_price": 700000,
            "is_promo": True,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Finition crème nacré et or royal avec applique veilleuse LED murale intégrée, armoire arche miroir, commode coiffeuse design. Pose offerte.",
            "description": "Le Modèle 6650# apporte une ambiance d'hôtel 5 étoiles à votre chambre avec sa tête de lit capitonnée alvéolée munie de veilleuses lumineuses chaleureuses et de baguettes dorées étincelantes.\n\nEnsemble complet avec lit King 3 places, armoire avec miroir en arche, coiffeuse et chevets.\nLivraison et montage inclus à Bamako.",
            "features": ["Appliques veilleuses LED d'ambiance", "Arche miroir centrale sur armoire", "Lit King 3 places grand confort", "Livraison et pose gratuites à Bamako"],
            "images": ["media_1795868531357_0b9efa49.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-923",
            "name": "Chambre à Coucher 3 Places Prestige Veilleuse Digitale Modèle 923#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 649000,
            "old_price": 700000,
            "is_promo": True,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Style royal blanc et dorures géométriques, rétroéclairage LED sur tête de lit et miroir coiffeuse. Lit 3 places, armoire 5 portes, coiffeuse.",
            "description": "Majestueuse chambre complète Modèle 923# en blanc éclatant et arabesques dorées.\nElle se distingue par ses éclairages d'ambiance LED digitaux intégrés dans la tête de lit et autour du miroir coiffeuse.\n\nService VIP Onizuka Shop : Livraison et montage clé en main offerts à Bamako.",
            "features": ["Éclairage LED d'ambiance tête de lit et miroir", "Arabesques et liserés dorés", "Grand lit 3 places", "Armoire dressing spacieuse", "Installation incluse"],
            "images": ["media_1795868550127_59ba4791.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-8807",
            "name": "Chambre à Coucher Complète 3 Places Design LED Modèle 8807#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 649000,
            "old_price": 700000,
            "is_promo": True,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Combinaison blanc mat et noyer chaud avec appliques lumineuses intégrées, claustras dorés sur armoire et commode. Montage offert.",
            "description": "Le Modèle 8807# allie la douceur du blanc et la noblesse du noyer avec des claustras dorés artistiques et des luminaires de chevet intégrés directement dans le dosseret.\n\nComprend le lit 3 places, l'armoire dressing avec miroirs, la commode coiffeuse et les 2 chevets.\nLivraison et installation offertes à Bamako.",
            "features": ["Veilleuses intégrées au chevet", "Claustras dorés graphiques", "Lit 3 places ergonomique", "Livraison & pose offertes à Bamako"],
            "images": ["media_1795868574306_5a766cd4.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-922",
            "name": "Chambre à Coucher Complète 3 Places Impériale Veilleuse LED Modèle 922#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 649000,
            "old_price": 700000,
            "is_promo": True,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Chambre impériale blanc nacré et baguettes d'or, chevet géométrique avec appliques LED intégrées, coiffeuse miroir LED rétroéclairé.",
            "description": "Offrez-vous un palace à domicile avec le Modèle 922#. Sa tête de lit capitonnée blanc crème est encadrée de panneaux lumineux LED d'ambiance et de dorures géométriques.\n\nPack complet avec lit 3 places, armoire dressing multi-portes, coiffeuse et 2 tables de nuit.\nMontage et installation offerts à Bamako.",
            "features": ["Tête de lit rétroéclairée LED", "Miroir coiffeuse LED", "Finitions blanc et dorures nobles", "Livraison et installation gratuites"],
            "images": ["media_1795868581322_6de1a558.jpg"]
        }
    ]
    for b in bedrooms_649k:
        create_product(b, b['images'])

    # ==========================================
    # 6. Réfrigérateur combiné Étoile XRD-140 (140 Litres) - 180 000 FCFA
    # ==========================================
    create_product({
        "sku": "ETOILE-XRD-140",
        "name": "Réfrigérateur Combiné Étoile 140 Litres XRD-140 Nature Fresh",
        "category": cat_refrig,
        "brand": b_etoile,
        "price": 180000,
        "badge": "Combiné 3 Tiroirs",
        "short_description": "Réfrigérateur combiné 140L Étoile XRD-140 avec congélateur bas à 3 tiroirs transparents indépendants, régulateur de tension intégré et classe A+.",
        "description": "Le réfrigérateur combiné Étoile XRD-140 Nature Fresh est l'appareil idéal pour conserver vos aliments frais et congelés de façon ordonnée.\n\n- Capacité brute de 140 Litres\n- Partie haute : réfrigérateur avec clayettes en verre trempé et bac à légumes\n- Partie basse : congélateur performant 4 étoiles avec 3 tiroirs indépendants transparents\n- Régulateur de tension intégré (protège contre les variations de courant)\n- Compresseur fiable et super économique (150 kWh/an)\n- Serrure avec clé de sécurité\n- Finition silver moderne.",
        "features": ["Capacité 140 Litres", "Congélateur bas 3 tiroirs indépendants", "Régulateur de tension intégré", "Classe énergétique A+ Super Économique", "Serrure à clé"],
    }, ["media_1795868658498_a37b600f.jpg", "media_1795868664452_26f23caa.jpg", "media_1795868671882_38367ca8.jpg"])

    # ==========================================
    # 7. Réfrigérateur Étoile XRD-128 combiné 128L - 139 000 FCFA
    # ==========================================
    create_product({
        "sku": "ETOILE-XRD-128",
        "name": "Réfrigérateur Combiné Étoile 128 Litres XRD-128 Nature Fresh",
        "category": cat_refrig,
        "brand": b_etoile,
        "price": 139000,
        "badge": "Format Slim 148cm",
        "short_description": "Réfrigérateur combiné 128L Étoile XRD-128 (H:1480 mm, L:483 mm, P:475 mm). Congélateur bas 3 tiroirs, régulateur de tension, super économique 142 kWh/an.",
        "description": "Le combiné Étoile XRD-128 offre un ratio encombrement/capacité remarquable grâce à son format slim élégant (148 cm de hauteur).\n\n- Capacité totale de 128 Litres\n- Réfrigérateur supérieur avec clayettes en verre trempé réglables et bac fraîcheur\n- Congélateur inférieur avec 3 compartiments tiroirs transparents pour un rangement optimal de la viande et du poisson\n- Protection intégrée contre les surtensions\n- Consommation record de seulement 142 kWh/an\n- Serrure de sécurité et éclairage intérieur LED.",
        "features": ["Capacité 128 Litres", "Dimensions : H 148 cm x L 48.3 cm x P 47.5 cm", "Congélateur bas 3 tiroirs", "Régulateur de tension", "Consommation 142 kWh/an"],
    }, ["media_1795868753254_b1989a66.jpg", "media_1795868759338_8950f5f9.jpg", "media_1795868769154_d0a2b9b7.jpg"])

    # ==========================================
    # 8. Réfrigérateur bar 2 portes Étoile XRD-100 (100L) - 90 000 FCFA
    # ==========================================
    create_product({
        "sku": "ETOILE-XRD-100",
        "name": "Réfrigérateur Bar Double Porte Étoile 100 Litres XRD-100",
        "category": cat_refrig,
        "brand": b_etoile,
        "price": 90000,
        "badge": "Double Porte Compact",
        "short_description": "Frigo bar 2 portes 100L Étoile XRD-100 (H:865 mm, L:449 mm, P:440 mm). Vrai compartiment congélateur séparé, régulateur de tension, serrure.",
        "description": "Le réfrigérateur bar Étoile XRD-100 est une innovation pratique : il offre deux portes séparées dans un format ultra-compact de 86.5 cm de haut.\n\n- Capacité de 100 Litres\n- Véritable congélateur haut indépendant avec porte dédiée\n- Réfrigérateur bas avec étagères verre trempé, bac fraîcheur et balconnets\n- Régulateur de tension protecteur intégré\n- Consommation ultra-basse 128 kWh/an\n- Serrure de sécurité à clé\n- Idéal pour chambres d'hôtel, studios, bureaux et chambres parentales.",
        "features": ["Capacité 100 Litres", "Double porte avec vrai congélateur séparé", "Hauteur 86.5 cm x Largeur 44.9 cm", "Régulateur de tension", "Serrure à clé"],
    }, ["media_1795868785862_9eaf6cb8.jpg"])

    # ==========================================
    # 9. Réfrigérateur bar 1 porte Étoile XR-100 (100L) - 79 000 FCFA
    # ==========================================
    create_product({
        "sku": "ETOILE-XR-100",
        "name": "Réfrigérateur Bar 1 Porte Étoile 100 Litres XR-100",
        "category": cat_refrig,
        "brand": b_etoile,
        "price": 79000,
        "badge": "Super Éco 84 kWh",
        "short_description": "Frigo bar 1 porte 100L Étoile XR-100 avec compartiment freezer intérieur, clayettes réglables, serrure de sécurité et consommation record de 84 kWh/an.",
        "description": "Le frigo bar 1 porte Étoile XR-100 est le modèle le plus économique de sa catégorie.\n\n- Volume de 100 Litres bien agencé\n- Compartiment freezer supérieur pour glaçons et fraîcheur intense\n- 3 clayettes réglables en verre trempé + bac à légumes\n- Consommation ultra-faible de seulement 84 kWh/an\n- Régulateur de tension intégré contre les coupures\n- Serrure de fermeture à clé.",
        "features": ["Capacité 100 Litres", "1 porte avec compartiment freezer", "Consommation ultra-faible 84 kWh/an", "Régulateur de tension", "Serrure de sécurité"],
    }, ["media_1795868810141_7130474e.jpg", "media_1795868824655_8900f1d2.jpg", "media_1795868829967_647f6e6b.jpg"])

    # ==========================================
    # 10. Sonifer Plaque à infrarouge 1 feux SF-3043 (38 000 FCFA)
    # ==========================================
    create_product({
        "sku": "SONIFER-SF-3043",
        "name": "Plaque de Cuisson Infrarouge Céramique 1 Feu Sonifer SF-3043 (2000W)",
        "category": cat_electromenager,
        "brand": b_sonifer,
        "price": 38000,
        "badge": "Puissance 2000W",
        "short_description": "Plaque vitrocéramique à infrarouge 1 foyer Sonifer SF-3043 2000W. Compatible avec TOUS types de casseroles (inox, fer, céramique, alu, verre). Minuteur et commandes tactiles.",
        "description": "Cuisinez rapidement et sans contrainte avec la plaque à induction infrarouge céramique Sonifer SF-3043.\n\n- Puissance de chauffe instantanée 2000W\n- Technologie infrarouge céramique : fonctionne avec absolument TOUS les récipients (pas besoin de casseroles spéciales induction !)\n- Surface en verre microcristallin haute résistance facile à nettoyer\n- Écran digital LED avec contrôle tactile et thermostat rotatif précis\n- Minuteur réglable et arrêt automatique de sécurité\n- Poignées latérales en acier pour une manipulation sans risque.",
        "features": ["Puissance 2000W", "Compatible TOUTES casseroles", "Surface vitrocéramique microcristalline", "Contrôle tactile + thermostat", "Minuteur et sécurité surchauffe"],
    }, ["media_1795868906326_81b3214e.jpg"])

    # ==========================================
    # 11. Coiffeuses simples avec lumière LED digitale (122 000 FCFA)
    # Modèle 903# et Modèle 896#
    # ==========================================
    coiffeuses = [
        {
            "sku": "COIFFEUSE-LED-903",
            "name": "Coiffeuse Moderne avec Miroir Ovale LED Tactile Modèle 903# (avec Tabouret)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 122000,
            "badge": "Miroir LED Tactile",
            "short_description": "Coiffeuse élégante blanc nacré avec grand miroir ovale rétroéclairé LED tactile, meuble de rangement vertical intégré, tiroirs et tabouret rembourré inclus.",
            "description": "La coiffeuse Modèle 903# sublime votre espace beauté avec son miroir ovale entouré d'un anneau lumineux LED à intensité réglable.\n\n- Grand miroir ovale haute définition avec éclairage LED tactile\n- Rangement vertical avec étagères et vitrine pour parfums et cosmétiques\n- Grand plateau avec tiroir et caisson latéral à porte battante\n- Livrée avec son tabouret assorti rembourré en similicuir\n- Finition blanc éclatant et poignées dorées raffinées.",
            "features": ["Miroir ovale LED à intensité réglable", "Tabouret rembourré inclus", "Colonne de rangement parfums & soins", "Tiroirs coulissants et caisson bas"],
            "images": ["media_1795868924892_2390ce19.jpg"]
        },
        {
            "sku": "COIFFEUSE-LED-896",
            "name": "Coiffeuse Moderne Géométrique Miroir Hexagonal LED Modèle 896# (avec Tabouret)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 122000,
            "badge": "Miroir LED Tactile",
            "short_description": "Coiffeuse contemporaine blanc & bleu ardoise, miroir biseauté hexagonal LED, vitrine ronde avec éclairage intérieur, tiroirs et tabouret.",
            "description": "Avec son design bicolore blanc et gris-bleu ardoise, la coiffeuse Modèle 896# apporte une touche moderne et graphique à votre chambre.\n\n- Miroir hexagonal bordé d'un ruban LED haute luminosité\n- Vitrine ronde hublot design pour exposer vos plus beaux flacons\n- Large plan de travail imitation marbre avec tiroirs et caisson de rangement\n- Tabouret design confortable inclus.",
            "features": ["Miroir hexagonal rétroéclairé LED", "Vitrine hublot ronde intégrée", "Tabouret assorti inclus", "Poignées et motifs dorés"],
            "images": ["media_1795868930445_f8a3e064.jpg"]
        }
    ]
    for c in coiffeuses:
        create_product(c, c['images'])

    # ==========================================
    # 12. Salles à manger 4 places surface en vitre (105 000 FCFA)
    # 3 modèles distincts
    # ==========================================
    dining_glass = [
        {
            "sku": "SAM-VITRE-CAFE-01",
            "name": "Salle à Manger 4 Places Plateau Verre Trempé Décor Café & Nuances",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 105000,
            "badge": "Verre Trempé Décor",
            "short_description": "Ensemble table à manger 4 places avec plateau en verre trempé sérigraphié motifs café lounge et 4 chaises en métal renforcé avec assises similicuir noir.",
            "description": "Cet ensemble salle à manger 4 places apporte une ambiance bistrot chic et moderne à votre salon ou cuisine.\n\n- Table avec plateau en verre trempé résistant aux chocs et à la chaleur, décor café artistique\n- Structure robuste en acier tubulaire noir thermolaqué\n- 4 chaises confortables avec dossier ergonomique ajouré et assise rembourrée en similicuir noir facile d'entretien\n- Dimensions idéales pour les espaces conviviaux.",
            "features": ["Table 4 places + 4 chaises", "Plateau verre trempé décor café", "Structure métal noir haute résistance", "Assises rembourrées similicuir noir"],
            "images": ["media_1795868950776_b9308328.jpg"]
        },
        {
            "sku": "SAM-VITRE-NOIR-LIGNES-02",
            "name": "Salle à Manger 4 Places Plateau Verre Trempé Noir & Bandes Miroir",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 105000,
            "badge": "Verre Noir & Miroir",
            "short_description": "Ensemble table 4 chaises avec plateau en verre trempé noir laqué rehaussé de deux bandes dépolies effet miroir. Chaises métal noir.",
            "description": "Un ensemble salle à manger 4 places au design minimaliste et sophistiqué.\n\n- Plateau en verre trempé noir brillant avec doubles lignes miroir centrales\n- Piétement stable et solide en métal noir\n- 4 chaises ergonomiques avec assises confortables\n- Très facile à nettoyer au quotidien.",
            "features": ["Plateau verre trempé noir et bandes miroir", "4 chaises métal noir assorties", "Conception solide et stable", "Entretien facile en un coup d'éponge"],
            "images": ["media_1795868956869_7de515ab.jpg"]
        },
        {
            "sku": "SAM-VITRE-MULTI-WAVE-03",
            "name": "Salle à Manger 4 Places Plateau Verre Trempé Noir Motifs Vagues Colorées",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 105000,
            "badge": "Design Vagues Color",
            "short_description": "Table à manger 4 places en verre trempé noir sublimé par des arabesques lumineuses multicolores et fleur d'eau. 4 chaises noires incluses.",
            "description": "Apportez de la gaité et de l'éclat à vos repas familiaux avec cette table 4 places au plateau en verre trempé imprimé de volutes lumineuses multicolores.\n\n- Plateau verre trempé sécurit épais et résistant\n- 4 chaises solides en acier laqué noir avec assises confortables\n- Idéale pour cuisine, salle à manger ou véranda.",
            "features": ["Verre trempé sérigraphie vagues colorées", "4 chaises en acier noir avec assise similicuir", "Design original et contemporain"],
            "images": ["media_1795868971467_2ac9ed76.jpg"]
        }
    ]
    for d in dining_glass:
        create_product(d, d['images'])

    # ==========================================
    # 13. Salles à manger 4 places surface en bois (120 000 FCFA)
    # 6 modèles/finitions distincts
    # ==========================================
    dining_wood = [
        {
            "sku": "SAM-BOIS-MARBRE-AMBRE-01",
            "name": "Salle à Manger 4 Places Plateau Bois Finition Marbre Ambré",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Finition Ambre & Or",
            "short_description": "Table 4 places plateau bois lourd mélaminé décor marbre ambre chaleureux, structure métal noir avec grille de rangement et 4 chaises.",
            "description": "L'ensemble salle à manger Modèle Marbre Ambré allie le toucher robuste du bois et l'éclat des veinures marbrées dorées.\n\n- Plateau en bois mélaminé haute densité résistant aux rayures et liquides\n- Grille de rangement sous plateau pratique pour sets de table ou revues\n- 4 chaises en métal noir avec assise similicuir haute qualité.",
            "features": ["Plateau bois décor marbre ambré", "Grille de rangement sous-tablette", "Structure métal robuste", "4 chaises confort incluses"],
            "images": ["media_1795868989655_2a7a297f.jpg"]
        },
        {
            "sku": "SAM-BOIS-ACAJOU-CHENE-02",
            "name": "Salle à Manger 4 Places Plateau Bois Massif Finition Acajou / Noyer",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Bois Noyer Élégance",
            "short_description": "Table 4 places plateau bois ton acajou / noyer foncé chaleureux avec étagère panier inférieure et 4 chaises métal noir.",
            "description": "Un style classique et noble avec ce plateau bois aux teintes noyer foncé / acajou.\nParfaitement stable avec ses pieds métalliques solides, cette table offre une grande durabilité et un confort d'assise supérieur.",
            "features": ["Finition noyer / acajou noble", "Panier de rangement intégré sous plateau", "4 chaises robustes", "Entretien simple"],
            "images": ["media_1795869035732_f3aaf2c9.jpg"]
        },
        {
            "sku": "SAM-BOIS-MARBRE-BLANC-03",
            "name": "Salle à Manger 4 Places Plateau Bois Finition Marbre Blanc Piétement Blanc",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Marbre Blanc & Piétement Blanc",
            "short_description": "Table 4 places lumineuse avec plateau bois décor marbre blanc de Carrare et piétement tubulaire blanc, accompagnée de 4 chaises noires bicolores.",
            "description": "Une alliance chic et contrastée de blanc immaculé et de noir moderne.\nLe plateau bois décor marbre blanc veiné gris illumine immédiatement la pièce tout en restant très chaleureux au toucher.",
            "features": ["Plateau bois marbre blanc de Carrare", "Piétement acier blanc laqué", "4 chaises noires confortables", "Look scandinave moderne"],
            "images": ["media_1795869043035_654bf57f.jpg"]
        },
        {
            "sku": "SAM-BOIS-CHENE-CLAIR-04",
            "name": "Salle à Manger 4 Places Plateau Bois Chêne Clair Naturel",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Chêne Clair Scandinave",
            "short_description": "Table 4 places plateau bois veiné chêne clair naturel, structure métal noir et 4 chaises avec assises noires ergonomiques.",
            "description": "Apportez une touche scandinave douce et naturelle avec ce modèle en chêne clair.\nSon plateau bois épais est agréable, résistant et s'adapte à tous les styles de décoration intérieure.",
            "features": ["Plateau chêne clair chaleureux", "Structure métal noir avec panier inférieur", "4 chaises confortables"],
            "images": ["media_1795869052869_8b446611.jpg"]
        },
        {
            "sku": "SAM-BOIS-MARBRE-GRIS-05",
            "name": "Salle à Manger 4 Places Plateau Bois Finition Marbre Gris Impérial",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Marbre Gris Impérial",
            "short_description": "Table 4 places plateau bois décor marbre gris minéral texturé, piétement métal noir avec étagère basse et 4 chaises.",
            "description": "Le décor marbre gris impérial confère à cette table un cachet minéral d'un luxe sobre et indémodable.\nLa finition mélaminée haute protection résiste aux taches et aux frottements du quotidien.",
            "features": ["Finition marbre gris minéral texturé", "Cadre en acier noir renforcé", "4 chaises coordonnées avec assises rembourrées"],
            "images": ["media_1795869059526_1a2a7c65.jpg"]
        },
        {
            "sku": "SAM-BOIS-MARBRE-NOIR-06",
            "name": "Salle à Manger 4 Places Plateau Bois Finition Marbre Noir Marquina",
            "category": cat_salle_manger,
            "brand": b_onizuka,
            "price": 120000,
            "badge": "Marbre Noir Étoilé",
            "short_description": "Table 4 places plateau bois finition marbre noir veiné blanc de prestige, cadre métal noir et 4 chaises tout noir.",
            "description": "L'élégance absolue du noir profond rehaussé de veinures blanches façon marbre Marquina.\nUn ensemble complet à la fois robuste, moderne et très facile à vivre au quotidien.",
            "features": ["Plateau bois marbre noir Marquina", "Allure 100% noir prestige", "4 chaises confortables avec dossier à barreaux"],
            "images": ["media_1795869067430_21d13c88.jpg"]
        }
    ]
    for d in dining_wood:
        create_product(d, d['images'])

    # ==========================================
    # 14. Samsung TV 85" Mini-LED M70HD (1 025 000 FCFA)
    # ==========================================
    create_product({
        "sku": "SAM-TV-85-M70HD",
        "name": "Smart TV Samsung 85\" Mini-LED 4K UHD Modèle 2026 M70HD",
        "category": cat_tv,
        "brand": b_samsung,
        "price": 1025000,
        "is_featured": True,
        "badge": "Mini-LED 2026 (85\")",
        "short_description": "Écran géant 85 pouces (215 cm) Samsung Mini-LED 4K Ultra HD Modèle 2026 M70HD. Technologie Ultimate Mini LED Dimming, Smart TV Tizen OS, Wi-Fi 6, 3 ports HDMI, Dolby Audio.",
        "description": "Vivez l'expérience ultime du cinéma à la maison avec le téléviseur géant Samsung 85 pouces Mini-LED Modèle 2026 (Série M70HD).\n\n- Diagonale gigantesque de 85 pouces (215 cm) de classe cinéma\n- Technologie Ultimate Mini LED Dimming : contraste infini, noirs absolus et luminosité éclatante grâce aux milliers de micro-diodes\n- Processeur 4K Upscaling intelligent pour convertir tous vos contenus en ultra haute définition\n- Système d'exploitation Tizen OS ultra-fluide avec toutes vos applications préférées (Netflix, YouTube, Prime Video, Disney+, etc.)\n- Connectivité ultra-rapide Wi-Fi 6 / 6E et 3 ports HDMI haute vitesse\n- Son optimisé Adaptive Sound avec Dolby Audio et suivi spatial OTS (Object Tracking Sound)\n- Télécommande intelligente et design ultra-fin sans bordure Frameless.",
        "features": ["Écran géant 85\" (215 cm)", "Technologie Mini-LED Dimming", "Résolution 4K Ultra HD", "Smart TV Tizen OS avec Wi-Fi 6", "Son Dolby Audio & Adaptive Sound"],
    }, ["media_1795869133381_49172eec.jpg"])

    # ==========================================
    # 15. Samsung TV 75" Mini-LED M70HD (790 000 FCFA)
    # ==========================================
    create_product({
        "sku": "SAM-TV-75-M70HD",
        "name": "Smart TV Samsung 75\" Mini-LED 4K UHD Modèle 2026 M70HD",
        "category": cat_tv,
        "brand": b_samsung,
        "price": 790000,
        "is_featured": True,
        "badge": "Mini-LED 2026 (75\")",
        "short_description": "Téléviseur 75 pouces (189 cm) Samsung Mini-LED 4K Ultra HD Série 2026 M70HD. Rétroéclairage Mini LED, Tizen OS, Wi-Fi 6, Dolby Audio, 3 HDMI.",
        "description": "L'excellence visuelle Samsung dans un format majestueux de 75 pouces (189 cm).\nDoté de la technologie d'affichage de pointe Mini-LED, le modèle 2026 Samsung M70HD procure des couleurs d'une vivacité spectaculaire (Color Booster) et un contraste saisissant.\n\n- Écran 75 pouces 4K UHD Mini-LED\n- Système Tizen OS connecté Wi-Fi 6\n- Son immersif Dolby Audio\n- Garantie officielle Onizuka Shop.",
        "features": ["Écran 75\" (189 cm)", "Dalle Mini-LED 4K UHD", "Système connecté Tizen OS", "Wi-Fi 6 et 3x HDMI", "Dolby Audio certifié"],
    }, ["media_1795869145967_24cfcfed.jpg"])

    # ==========================================
    # 16. Chambres à Coucher 3 places avec veilleuse LED digitale (670 000 FCFA)
    # 5 modèles : 9056#, 110#, 9047#, KD-316#, MC2203#
    # ==========================================
    bedrooms_670k = [
        {
            "sku": "CHAMBRE-LED-9056",
            "name": "Chambre à Coucher Complète 3 Places Luxe & Bout de Lit Coffre Modèle 9056# (670k)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 670000,
            "badge": "Bout de Lit Coffre Inclus",
            "is_featured": True,
            "short_description": "Ensemble complet avec banc coffre de lit rembourré intégré, appliques veilleuses LED rondes, armoire 4 portes avec miroirs centraux et commode géométrique.",
            "description": "Le Modèle 9056# se distingue par son banc coffre capitonné en bout de lit apportant un confort exceptionnel et un vaste espace de rangement dissimulé.\nTête de lit majestueuse avec appliques lumineuses LED intégrées.\n\nLivraison et installation offertes à Bamako.",
            "features": ["Bout de lit banquette coffre inclus", "Veilleuses d'ambiance LED intégrées", "Armoire dressing 4 portes avec miroirs", "Pose et livraison gratuites à Bamako"],
            "images": ["media_1795869164811_3d5a2ac8.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-110",
            "name": "Chambre à Coucher Complète 3 Places Royale Blanc & Or Modèle 110# (670k)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 670000,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Style château moderne en blanc laqué pur et arches dorées. Appliques veilleuses intégrées, coiffeuse à miroir LED tactile et armoire 4 portes.",
            "description": "L'ensemble Modèle 110# évoque la pureté et la royauté avec ses lignes d'or cintrées et son dosseret illuminé de lampes veilleuses LED intégrées.\n\nComprend le grand lit 3 places, l'armoire dressing avec miroirs, la coiffeuse miroir LED et le tabouret.\nLivraison et installation soignées gratuites à Bamako.",
            "features": ["Veilleuses d'ambiance intégrées", "Dorures royales cintrées", "Coiffeuse avec miroir LED et tabouret", "Livraison et montage inclus"],
            "images": ["media_1795869176452_e7593b43.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-9047",
            "name": "Chambre à Coucher Complète 3 Places Design Ovale LED Modèle 9047# (670k)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 670000,
            "badge": "Bout de Lit Coffre Inclus",
            "short_description": "Tête de lit ovale avec ruban LED rétroéclairé, bout de lit avec tiroirs coffre, armoire contemporaine grise & or et coiffeuse miroir LED.",
            "description": "Le Modèle 9047# allie modernité graphique et confort absolu grâce à son médaillon central capitonné rétroéclairé par un bandeau LED doux.\nInclus une banquette de lit coffre multifonctionnelle.\n\nInstallation gratuite à Bamako.",
            "features": ["Bandeau LED ovale rétroéclairé", "Bout de lit coffre à tiroirs", "Armoire dressing contemporaine", "Installation offerte"],
            "images": ["media_1795869203126_e0c5286b.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-KD316",
            "name": "Chambre à Coucher Complète 3 Places Écrin Crème & Or Modèle KD-316# (670k)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 670000,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Tête de lit capitonnée à motifs géométriques avec appliques veilleuses LED, armoire 4 portes à claustras latéraux dorés et coiffeuse miroir LED.",
            "description": "Le Modèle KD-316# crée une atmosphère feutrée et luxueuse grâce à ses claustras dorés latéraux et ses veilleuses LED douces de chaque côté du lit.\n\nLivraison et montage offerts à Bamako.",
            "features": ["Appliques LED veilleuses intégrées", "Claustras dorés géométriques", "Armoire dressing 4 portes avec miroirs", "Montage offert"],
            "images": ["media_1795869212584_ec862cf0.jpg"]
        },
        {
            "sku": "CHAMBRE-LED-MC2203-670",
            "name": "Chambre à Coucher Complète 3 Places Grand Luxe Modèle MC2203# (670k)",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 670000,
            "badge": "Veilleuse LED Digitale",
            "short_description": "Tête de lit capitonnée haute avec gorges lumineuses LED verticales, armoire 4 portes laquée crème avec bandes dorées diagonales et coiffeuse LED.",
            "description": "Le Modèle MC2203# séduit par ses jeux de lumières verticaux intégrés dans la tête de lit et ses motifs dorés en chevrons sur l'armoire dressing.\n\nPack complet avec lit 3 places, armoire, coiffeuse miroir LED et 2 chevets.\nLivraison et installation incluses à Bamako.",
            "features": ["Colonnes lumineuses LED verticales", "Motifs chevrons dorés", "Grand lit 3 places", "Livraison & pose offertes"],
            "images": ["media_1795869220169_de52425a.jpg"]
        }
    ]
    for b in bedrooms_670k:
        create_product(b, b['images'])

    # ==========================================
    # 17. Matelas Grand Confort (3 épaisseurs/variantes)
    # Épaisseur 20 avec fer = 138k
    # Épaisseur 25 avec fer = 152k
    # Épaisseur 25 sans fer = 172k
    # ==========================================
    matelas_list = [
        {
            "sku": "MATELAS-CONF-EP20-FER",
            "name": "Matelas Orthopédique Grand Confort Épaisseur 20 cm (Ressorts avec Fer)",
            "category": cat_matelas,
            "brand": b_onizuka,
            "price": 138000,
            "badge": "Épaisseur 20 cm",
            "short_description": "Matelas 2 ou 3 places grand confort épaisseur 20 cm avec carcasse à ressorts en acier renforcé (avec fer), tissu piqué hypoallergénique respirant.",
            "description": "Le matelas grand confort épaisseur 20 cm avec ressorts métalliques renforcés offre un excellent soutien de la colonne vertébrale pour un sommeil réparateur à prix très doux.\n\n- Épaisseur : 20 cm\n- Suspension à ressorts biconiques en acier trempé de haute résistance\n- Garnissage mousse confort et nappe feutre isolante\n- Coutil piqué stretch doux, respirant et traité anti-acariens.",
            "features": ["Épaisseur 20 cm", "Structure ressorts avec fer renforcé", "Soutien ferme et équilibré", "Tissu respirant hypoallergénique"],
            "images": ["media_1795869265175_955ee19a.jpg"]
        },
        {
            "sku": "MATELAS-CONF-EP25-FER",
            "name": "Matelas Orthopédique Grand Confort Épaisseur 25 cm (Ressorts avec Fer)",
            "category": cat_matelas,
            "brand": b_onizuka,
            "price": 152000,
            "badge": "Épaisseur 25 cm",
            "short_description": "Matelas prestige épaisseur 25 cm avec armature ressorts acier renforcé (avec fer), accueil moelleux et soutien dorsal optimal.",
            "description": "Avec ses 25 cm d'épaisseur généreuse, ce matelas à ressorts métalliques assure une durabilité accrue et un confort de couchage digne des grands hôtels.\n\n- Épaisseur : 25 cm\n- Carcasse ressorts en acier avec cadre de maintien périphérique\n- Couches de mousse haute résilience pour un accueil enveloppant\n- Tissu piqué de luxe respirant.",
            "features": ["Épaisseur 25 cm", "Suspension à ressorts acier avec fer", "Confort d'hôtel de luxe", "Anti-affaissement"],
            "images": ["media_1795869265175_955ee19a.jpg"]
        },
        {
            "sku": "MATELAS-CONF-EP25-SANSFER",
            "name": "Matelas Mémoire de Forme / Mousse Haute Densité 25 cm (Sans Fer)",
            "category": cat_matelas,
            "brand": b_onizuka,
            "price": 172000,
            "badge": "100% Mousse Sans Fer (25 cm)",
            "is_featured": True,
            "short_description": "Matelas haut de gamme épaisseur 25 cm entièrement en mousse haute densité / mémoire de forme (sans ressorts métalliques), zéro vibration, confort absolu.",
            "description": "Le summum de la literie moderne : le matelas 25 cm SANS FER (sans aucun ressort métallique).\nEntièrement constitué de mousses orthopédiques haute densité de dernière génération, il épouse parfaitement les contours du corps et isole complètement les mouvements pour un sommeil paisible sans aucune secousse.\n\n- Épaisseur : 25 cm\n- 100% mousse orthopédique haute densité & accueil confort\n- Zéro bruit et indépendance de couchage totale\n- Recommandé pour soulager les douleurs lombaires et articulaires.",
            "features": ["Épaisseur 25 cm", "100% Mousse haute densité (Sans fer)", "Indépendance de couchage totale", "Soutien anatomique optimal"],
            "images": ["media_1795869265175_955ee19a.jpg"]
        }
    ]
    for m in matelas_list:
        create_product(m, m['images'])

    # ==========================================
    # 18. Chambres à Coucher 3 places avec veilleuse LED digitale (700 000 FCFA)
    # 9 modèles de haute voltige
    # ==========================================
    bedrooms_700k = [
        {
            "sku": "CHAMBRE-700-MC2203",
            "name": "Chambre à Coucher Complète 3 Places Prestige Veilleuse LED Modèle MC2203# Crème",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "is_featured": True,
            "short_description": "Ensemble complet prestige avec lit 3 places, dosseret à rainures LED lumineuses, armoire dressing 4 portes avec motifs chevron d'or et coiffeuse miroir LED.",
            "description": "Le Modèle MC2203# représente le fleuron des chambres modernes en teinte crème royale et or ciselé.\nLivraison et montage complet offerts à Bamako.",
            "features": ["Tête de lit rétroéclairée LED", "Armoire 4 portes miroir et motifs dorés", "Coiffeuse avec miroir LED", "Montage et livraison inclus à Bamako"],
            "images": ["media_1795869288255_843ec4f2.jpg"]
        },
        {
            "sku": "CHAMBRE-700-KD309",
            "name": "Chambre à Coucher Complète 3 Places Design Arc Royal Modèle KD-309#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Dosseret rond capitonné gris ardoise cerclé d'or et de miroirs avec veilleuses LED intégrées, armoire dressing papillon dorée et coiffeuse.",
            "description": "Le Modèle KD-309# impressionne par sa tête de lit cintrée capitonnée de velours gris ardoise, auréolée d'arches dorées et de lanternes lumineuses LED.",
            "features": ["Dosseret capitonné demi-lune avec veilleuses", "Motifs sablier et papillon dorés sur armoire", "Lit 3 places grand format", "Pose gratuite"],
            "images": ["media_1795869293957_00ce3652.jpg"]
        },
        {
            "sku": "CHAMBRE-700-KD304",
            "name": "Chambre à Coucher Complète 3 Places Losange Or Modèle KD-304#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Tête de lit cintrée avec médaillon central en losange doré lumineux, armoire 4 portes et commode coiffeuse assorties.",
            "description": "L'ensemble KD-304# déploie une harmonie parfaite avec son emblème central en losange d'or illuminé par des réglettes LED douces.",
            "features": ["Médaillon central losange lumineux", "Armoire dressing 4 portes avec miroirs", "Installation incluse à Bamako"],
            "images": ["media_1795869301975_10631238.jpg"]
        },
        {
            "sku": "CHAMBRE-700-MC615",
            "name": "Chambre à Coucher Complète 3 Places Soleil Levant Or Modèle MC615#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Capitonnage soleil rayonnant avec veilleuses de chevet intégrées, armoire dressing à portes miroirs et colonnes dorées, coiffeuse LED.",
            "description": "Le motif en éventail rayonnant de la tête de lit confère au modèle MC615# une prestance sans égale.\nMontage et installation offerts.",
            "features": ["Tête de lit motif soleil rayonnant", "Veilleuses intégrées au lit", "Armoire et commode avec dorures", "Montage offert"],
            "images": ["media_1795869309775_3e090244.jpg"]
        },
        {
            "sku": "CHAMBRE-700-HN507",
            "name": "Chambre à Coucher Complète 3 Places Graphite & Argent Modèle HN-507#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Design moderne contemporain gris anthracite et noyer avec circuits graphiques argentés, appliques veilleuses LED et armoire 4 portes.",
            "description": "Le Modèle HN-507# s'adresse aux amateurs de design avant-gardiste avec ses volutes modernes argentées et son ambiance gris graphite.",
            "features": ["Finitions gris anthracite & circuits argent", "Appliques veilleuses LED intégrées", "Armoire dressing 4 portes avec miroirs"],
            "images": ["media_1795869316900_2f480d77.jpg"]
        },
        {
            "sku": "CHAMBRE-700-HN502",
            "name": "Chambre à Coucher Complète 3 Places Noyer & Or Étoilé Modèle HN-502#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Tête de lit horizontale avec luminaires de chevet dorés encastrés, armoire 4 portes noyer & graphite avec claustras ajourés et coiffeuse.",
            "description": "Le Modèle HN-502# associe la profondeur du noyer foncé à des panneaux rétroéclairés et des claustras dorés artistiques.",
            "features": ["Tête de lit panoramique avec veilleuses intégrées", "Claustras dorés sur armoire et commode", "Installation gratuite"],
            "images": ["media_1795869326633_09eb1d15.jpg"]
        },
        {
            "sku": "CHAMBRE-700-KD303",
            "name": "Chambre à Coucher Complète 3 Places Sablier Doré Modèle KD-303#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Tête de lit en faisceaux capitonnés avec appliques sabliers d'or lumineuses, armoire dressing 4 portes assortie et coiffeuse miroir LED.",
            "description": "Le Modèle KD-303# brille par ses colonnes dorées en forme de sablier qui diffusent une lumière apaisante des deux côtés du lit.",
            "features": ["Appliques sabliers dorés lumineuses", "Tête de lit capitonnée en faisceaux", "Armoire dressing 4 portes avec miroirs"],
            "images": ["media_1795869335184_914bbbc7.jpg"]
        },
        {
            "sku": "CHAMBRE-700-KD312",
            "name": "Chambre à Coucher Complète 3 Places Hexagones Dorés Modèle KD-312#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Tête de lit avec alvéoles hexagonales en résille d'or et appliques LED, armoire graphite avec poignées rosaces dorées et coiffeuse.",
            "description": "Le Modèle KD-312# offre une géométrie hexagonale fascinante mariée au gris graphite et aux reflets dorés chauds.",
            "features": ["Inserts alvéoles hexagonales en or", "Appliques veilleuses de nuit intégrées", "Armoire 4 portes grande capacité"],
            "images": ["media_1795869343696_382a33ff.jpg"]
        },
        {
            "sku": "CHAMBRE-700-KD307",
            "name": "Chambre à Coucher Complète 3 Places Lyre Royale Modèle KD-307#",
            "category": cat_chambre,
            "brand": b_onizuka,
            "price": 700000,
            "badge": "Prestige Veilleuse LED",
            "short_description": "Tête de lit galbée avec colonnes lumineuses cintrées, armoire dressing avec lyres dorées sur portes blanches et commode assortie.",
            "description": "Le Modèle KD-307# clôture cette collection prestige avec son motif inspiré de la lyre impériale sur fond blanc laqué pur.",
            "features": ["Motifs lyres dorées sculptées", "Tête de lit lumineuse galbée", "Livraison et pose offertes à Bamako"],
            "images": ["media_1795869350596_4308de92.jpg"]
        }
    ]
    for b in bedrooms_700k:
        create_product(b, b['images'])

    # ==========================================
    # 19. Moustiquaire électrique Winning Star ST-4037 3000V (26 000 FCFA)
    # ==========================================
    create_product({
        "sku": "WINSTAR-ST4037-3000V",
        "name": "Destructeur d'Insectes & Moustiquaire Électrique 3000V Winning Star ST-4037",
        "category": cat_maison,
        "brand": b_winning_star,
        "price": 26000,
        "badge": "Choc 3000V Écologique",
        "short_description": "Lampe anti-moustiques et destructeur d'insectes volant Winning Star ST-4037. Choc électrique haute tension 3000V en aluminium, couverture large surface, sans produits chimiques.",
        "description": "Protégez efficacement votre famille contre les moustiques et le paludisme sans odeur ni produit chimique avec la moustiquaire électrique professionnelle Winning Star ST-4037 (3000V).\n\n- Tube UV haute intensité attirant tous les moustiques, mouches et insectes volants\n- Grille électrique interne haute tension 3000V en aluminium pour une élimination instantanée\n- Large zone de couverture (Large Coverage Area) adaptée pour salon, chambre, véranda, restaurant ou boutique\n- Bac de récupération amovible lavable et chaîne de suspension fournie\n- 100% écologique et sans danger pour les enfants grâce à sa grille de protection extérieure.",
        "features": ["Puissance de choc 3000V", "Châssis aluminium robuste", "Sans odeur ni produits chimiques", "Large surface de protection", "Bac récepteur amovible facile à nettoyer"],
    }, ["media_1795869377212_91e0d03e.jpg"])

    # ==========================================
    # 20. Enceintes Haut-parleurs Boom (Okop & Winning Star)
    # 8013 (135k), 8010 (99k), 8011 (69k), 8006 (72k), 8004 (42k), 8007 (80k), ST-8101 (85k)
    # ==========================================
    boom_speakers = [
        {
            "sku": "OKOP-KP-8013",
            "name": "Enceinte Portable Bluetooth Boom OKOP KP-8013 High Power (500W)",
            "category": cat_audio,
            "brand": b_okop,
            "price": 135000,
            "badge": "Super Bass 500W",
            "is_featured": True,
            "short_description": "Enceinte boombox bluetooth géante OKOP KP-8013 (500W PMPO). Batterie monstre 16000mAh, étanche IPX6, cercles LED RGB pulsés, son 360° Surround Sound.",
            "description": "L'enceinte la plus puissante de la gamme OKOP : le modèle KP-8013 délivre un son explosif de 500W avec des basses profondes qui font trembler le sol.\n\n- Batterie rechargeable colossale de 16000 mAh (jusqu'à 15h d'autonomie non-stop et fonction Powerbank)\n- Norme d'étanchéité IPX6 résistante aux éclaboussures et à la pluie\n- Effets lumineux RGB dynamiques synchronisés sur la musique\n- Bluetooth 5.3 longue portée, entrées USB, carte TF, AUX et entrée micro.",
            "features": ["Puissance 500W", "Batterie 16000 mAh", "Étanche IPX6", "Effets lumineux RGB", "Son Hi-Fi Surround 360°"],
            "images": ["media_1795869427195_3b668540.jpg"]
        },
        {
            "sku": "OKOP-KP-8010",
            "name": "Enceinte Portable Bluetooth Boom OKOP KP-8010 Wireless Audio (250W)",
            "category": cat_audio,
            "brand": b_okop,
            "price": 99000,
            "badge": "Puissance 250W",
            "short_description": "Enceinte bluetooth portable OKOP KP-8010 (250W). Batterie 12000mAh, jeux de lumières RGB, son Hi-Fi Audio dynamique et poignée de transport ergonomique.",
            "description": "L'équilibre parfait entre puissance et transportabilité avec l'enceinte OKOP KP-8010.\n\n- Puissance de 250W avec double radiateur passif de basses\n- Batterie longue durée 12000 mAh\n- Lumières d'ambiance LED RGB\n- Connectivité complète Bluetooth, Clé USB et câble auxiliaire.",
            "features": ["Puissance 250W", "Batterie 12000 mAh", "Jeux de lumières RGB", "Double caisson de basses", "Son stéréo sans fil"],
            "images": ["media_1795869408224_a68c1091.jpg"]
        },
        {
            "sku": "OKOP-KP-8011",
            "name": "Enceinte Portable Bluetooth Boom OKOP KP-8011 High Power (150W)",
            "category": cat_audio,
            "brand": b_okop,
            "price": 69000,
            "badge": "Puissance 150W",
            "short_description": "Enceinte portable OKOP KP-8011 (150W). Batterie 5400mAh, anneaux LED RGB lumineux, son immersif Hi-Fi et format compact avec poignée intégrée.",
            "description": "L'enceinte idéale pour ambiancer vos sorties, pique-niques et soirées entre amis avec un son cristallin et des basses percutantes de 150W.",
            "features": ["Puissance 150W", "Batterie 5400 mAh", "Effets LED RGB", "Bluetooth rapide et stable"],
            "images": ["media_1795869415999_4af2a29a.jpg"]
        },
        {
            "sku": "BOOM-8006",
            "name": "Enceinte Bluetooth Boombox Stéréo Modèle 8006",
            "category": cat_audio,
            "brand": b_okop,
            "price": 72000,
            "badge": "Boombox Stéréo",
            "short_description": "Enceinte sans fil Boombox 8006 avec basses renforcées, éclairage LED party, entrée micro et batterie rechargeable grande autonomie.",
            "description": "Un son dynamique et percutant dans un format robuste conçu pour faire la fête partout.",
            "features": ["Basses profondes Extra Bass", "Batterie haute autonomie", "Bluetooth 5.0 / USB / TF", "Poignée de transport"],
            "images": ["media_1795869397551_55287e58.jpg"]
        },
        {
            "sku": "BOOM-8004",
            "name": "Enceinte Bluetooth Compacte Boom Modèle 8004",
            "category": cat_audio,
            "brand": b_okop,
            "price": 42000,
            "badge": "Format Nomade",
            "short_description": "Enceinte portable Boom 8004 compacte et puissante avec son stéréo clair, radio FM, lecteur USB/microSD et batterie longue durée.",
            "description": "La plus accessible et pratique de la série Boom : emportez votre musique partout avec vous avec une clarté sonore remarquable.",
            "features": ["Format ultra-portable", "Radio FM / USB / Carte SD", "Autonomie 8h", "Prix imbattable"],
            "images": ["media_1795869397551_55287e58.jpg"]
        },
        {
            "sku": "BOOM-8007",
            "name": "Enceinte Bluetooth Boombox Party Modèle 8007",
            "category": cat_audio,
            "brand": b_okop,
            "price": 80000,
            "badge": "Party Sound",
            "short_description": "Enceinte portable Boombox 8007 puissance intermédiaire avec égaliseur intégré, jeux de lumières disco et batterie haute capacité.",
            "description": "Conçue pour diffuser vos morceaux préférés avec fidélité et punch sonore pour toutes vos animations.",
            "features": ["Puissance et clarté acoustique", "Jeux de lumières dynamiques", "Entrée microphone pour karaoké"],
            "images": ["media_1795869397551_55287e58.jpg"]
        },
        {
            "sku": "WINSTAR-ST-8101",
            "name": "Enceinte Portable Party Box Winning Star ST-8101 (Nice Bass 6000mAh)",
            "category": cat_audio,
            "brand": b_winning_star,
            "price": 85000,
            "badge": "Party Box RGB",
            "is_featured": True,
            "short_description": "Enceinte sono portable Party Box Winning Star ST-8101 avec télécommande. Technologie Nice Bass Beat Audio, cercle lumineux RGB Flame, batterie 6000mAh (11.5h de lecture).",
            "description": "Mettez le feu à vos fêtes avec la Party Box Winning Star ST-8101 !\n\n- Technologie Nice Bass Beat Audio pour des basses rondes et puissantes\n- Cercle de lumière LED RGB interactif au rythme du son\n- Batterie rechargeable 7.4V / 6000 mAh offrant jusqu'à 11h30 de musique continue\n- Télécommande à distance fournie\n- Entrée micro / karaoké et Bluetooth haute fidélité.",
            "features": ["Technologie Nice Bass", "Batterie 6000 mAh (11.5h de jeu)", "Cercle LED RGB Party", "Télécommande incluse", "Entrée Micro & Guitare"],
            "images": ["media_1795869471451_b9394a7b.jpg"]
        }
    ]
    for spk in boom_speakers:
        create_product(spk, spk['images'])

    # ==========================================
    # 21. Sonifer Plaque de cuisson infrarouge 2 feux SF-3051 (68 000 FCFA)
    # ==========================================
    create_product({
        "sku": "SONIFER-SF-3051",
        "name": "Plaque de Cuisson Infrarouge Céramique Double Foyer Sonifer SF-3051 (1800W+1800W)",
        "category": cat_electromenager,
        "brand": b_sonifer,
        "price": 68000,
        "badge": "Double Foyer 3600W",
        "is_featured": True,
        "short_description": "Plaque vitrocéramique à infrarouge 2 feux Sonifer SF-3051 (1800W + 1800W = 3600W). Compatible TOUS types de casseroles, double affichage digital et thermostats indépendants.",
        "description": "La solution de cuisson moderne et ultra-rapide pour toute la famille : la table de cuisson vitrocéramique double foyer Sonifer SF-3051.\n\n- Deux foyers indépendants puissants de 1800W chacun (puissance totale cumulée 3600W)\n- Technologie infrarouge microcristalline résistante aux très hautes températures (jusqu'à 650°C)\n- Compatible avec ABSOLUMENT TOUS les types d'ustensiles : marmites en fonte, inox, poêles en aluminium, céramique, verre résistant\n- Réglage indépendant de chaque foyer avec boutons thermostats rotatifs et pavé tactile digital\n- Minuteur programmable et sécurité anti-surchauffe automatique\n- Poignées latérales en métal chromé pour un déplacement facile.",
        "features": ["Double feu indépendant 1800W + 1800W", "Compatible TOUTES marmites et poêles", "Panneau microcristallin haute résistance 650°C", "Double affichage digital LED + Minuteur", "Poignées en métal"],
    }, ["media_1795868847643_1d91c72c.jpg"])

    # ==========================================
    # 22. Chauffe-eau pour douche Milano (30L = 77 000 FCFA, 50L = 87 500 FCFA)
    # ==========================================
    water_heaters = [
        {
            "sku": "MILANO-EWH-30L",
            "name": "Chauffe-Eau Électrique de Douche Milano 30 Litres Haute Précision",
            "category": cat_sanitaire,
            "brand": b_milano,
            "price": 77000,
            "badge": "Thermostat Haute Précision",
            "short_description": "Chauffe-eau électrique mural Milano 30 Litres pour salle de bain. Cuve émaillée renforcée, thermostat de haute précision, protection surpression et norme étanchéité IPX4.",
            "description": "Profitez d'une douche chaude instantanée et délassante avec le chauffe-eau électrique Milano 30L.\n\n- Capacité de 30 Litres idéale pour célibataire ou couple\n- Thermostat haute précision pour ajuster la température idéale au degré près\n- Cuve interne traitée contre la corrosion et le calcaire\n- Soupape de sécurité contre les surpressions et coupure automatique thermique\n- Isolation thermique renforcée gardant l'eau chaude pendant de nombreuses heures.",
            "features": ["Capacité 30 Litres", "Thermostat haute précision", "Cuve émaillée anticorrosion", "Norme étanchéité IPX4", "Protection surchauffe et surpression"],
            "images": ["media_1795869488592_e2a86fc7.jpg"]
        },
        {
            "sku": "MILANO-EWH-50L",
            "name": "Chauffe-Eau Électrique de Douche Milano 50 Litres Haute Précision",
            "category": cat_sanitaire,
            "brand": b_milano,
            "price": 87500,
            "badge": "Grande Capacité Famille",
            "is_featured": True,
            "short_description": "Chauffe-eau électrique mural Milano 50 Litres. Grande réserve d'eau chaude pour toute la famille, thermostat haute précision, cuve renforcée et étanchéité IPX4.",
            "description": "Le chauffe-eau Milano 50 Litres assure un approvisionnement continu en eau chaude pour toute la maisonnée.\n\n- Capacité familiale de 50 Litres\n- Montée en température rapide et maintien au chaud prolongé\n- Système de sécurité multi-niveaux certifié aux normes internationales.",
            "features": ["Capacité familiale 50 Litres", "Thermostat haute précision", "Isolation thermique supérieure", "Protection sécurité IPX4"],
            "images": ["media_1795869488592_e2a86fc7.jpg"]
        }
    ]
    for wh in water_heaters:
        create_product(wh, wh['images'])

    # ==========================================
    # 23. Salle à manger luxe marbre 6 places (360 000 FCFA)
    # ==========================================
    create_product({
        "sku": "SAM-LUXE-MARBRE-6P",
        "name": "Ensemble Salle à Manger Grand Luxe Marbre Noir & 6 Fauteuils Cuir (360k)",
        "category": cat_salle_manger,
        "brand": b_onizuka,
        "price": 360000,
        "badge": "Luxe Marbre 6 Places",
        "is_featured": True,
        "short_description": "Table de salle à manger 6 places d'exception avec plateau marbre anthracite biseauté et 6 fauteuils ergonomiques en cuir gris avec surpiqûres sellier blanches et pieds métal.",
        "description": "Le prestige absolu pour votre salle à manger avec cet ensemble 6 places de haute facture.\n\n- Somptueuse table rectangulaire avec plateau en marbre anthracite satiné, parsemé de fines veinures dorées et cuivrées\n- Châssis architectural en acier lourd thermolaqué noir assurant une stabilité indéfectible\n- 6 fauteuils de table ergonomiques grand confort, habillés de cuir gris souris avec surpiqûres sellier blanches et coque enveloppante\n- Pieds de chaises fuselés en métal noir haute résistance\n- Un chef d'œuvre d'élégance et de convivialité pour vos réceptions et repas de famille.\n\nService VIP Onizuka Shop : Livraison et installation complètes offertes à Bamako.",
        "features": ["Table marbre anthracite satiné 6 places", "6 fauteuils grand confort cuir & surpiqûres sellier", "Piétement métal lourd renforcé", "Livraison et installation offertes à Bamako"],
    }, ["media_1795869245375_36f60984.jpg"])

    print("\n🎉 === IMPORTATION DE TOUS LES PRODUITS TERMINÉE AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    run_import()
