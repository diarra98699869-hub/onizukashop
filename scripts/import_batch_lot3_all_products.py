"""
Script d'importation Lot 3 Onizuka Shop :
- 9 Tableaux Décoratifs Triptyque 3 Pièces Grand Format Luxe (35 000 FCFA chacun)
- 3 Enceintes JBL Originales :
    * JBL Flip 7 (98 000 FCFA)
    * JBL Charge 5 (110 000 FCFA)
    * JBL Xtreme 4 (215 000 FCFA)
- 4 Réfrigérateurs Premium :
    * Réfrigérateur Combiné Pearl 370L Noir Vitré PF-370 avec Distributeur d'Eau (290 000 FCFA)
    * Réfrigérateur Combiné Hisense Inox avec Distributeur d'Eau (265 000 FCFA)
    * Réfrigérateur Combiné Roch 200 Litres 200DB Gris Anthracite (179 000 FCFA)
    * Réfrigérateur Bar Double Porte Vodacom 90 Litres Inox (99 000 FCFA)
- 5 Coffres-Forts Haute Sécurité & Ignifuges :
    * Coffre-Fort Ignifuge Lourd 105 kg Double Serrure (256 000 FCFA)
    * Coffre-Fort 75 kg Colonne Haute Sécurité Double Serrure Digitale & Clé (310 000 FCFA)
    * Coffre-Fort Ignifuge 55 kg Double Serrure (140 000 FCFA)
    * Coffre-Fort Blindé 30 kg Double Serrure Digitale (205 000 FCFA)
    * Coffre-Fort Compact Électronique 4 kg Serrure Numérique (65 000 FCFA)
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
        # Déjà présent sur le serveur (via Git ou import précédent)
        return f"products/{dest_filename}"
    
    src_path = USER_UPLOADED_DIR / src_name
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
        print(f"Image introuvable dans uploads ({src_path}) et media ({dest_path})")
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
                if i == 0 and not product.images.filter(is_primary=True).exists():
                    img_obj.is_primary = True
                    img_obj.save()

    status_str = "CRÉÉ" if created else "MIS À JOUR"
    displayed_price = sale_price if sale_price else regular_price
    print(f"[{status_str}] {product.name} ({displayed_price:,} FCFA) - SKU: {product.sku}")
    return product

def run_import():
    print("=== DÉBUT IMPORTATION DU LOT 3 DE NOUVEAUX PRODUITS ===")
    
    # --- 1. CATÉGORIES & MARQUES ---
    cat_meubles = get_or_create_cat("Meubles & Mobilier", icon="couch")
    cat_deco = get_or_create_cat("Tableaux & Décoration Murale", parent_slug=cat_meubles.slug, icon="palette")
    
    cat_audio = Category.objects.filter(slug='audio-enceintes-bluetooth').first() or get_or_create_cat("Audio & Enceintes Bluetooth", icon="music")
    cat_refrig = Category.objects.filter(slug='refrigerateurs-congelateurs').first() or get_or_create_cat("Réfrigérateurs & Congélateurs", icon="refrigerator")
    
    cat_protection = Category.objects.filter(slug='maison-protection').first() or get_or_create_cat("Maison & Protection", icon="shield")
    cat_coffres = get_or_create_cat("Coffres-Forts & Haute Sécurité", parent_slug=cat_protection.slug, icon="lock")

    # Marques
    b_onizuka_deco = get_or_create_brand("Onizuka Déco & Art")
    b_jbl = get_or_create_brand("JBL")
    b_pearl = get_or_create_brand("Pearl")
    b_hisense = get_or_create_brand("Hisense")
    b_roch = get_or_create_brand("Roch")
    b_vodacom = get_or_create_brand("Vodacom")
    b_safe = get_or_create_brand("Onizuka Sécurité")

    # --- 2. TABLEAUX DÉCORATIFS TRIPTYQUE (9 MODÈLES - 35 000 FCFA) ---
    tableaux = [
        {
            "sku": "TAB-3P-FEUILLAGE-OR-01",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Feuillage d'Or & Bleu Azur",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque mural luxe 3 panneaux, relief géométrique octogonal, feuillage or et argent, perle de cristal et ondes azur.",
            "description": "Sublimez votre salon, séjour ou chambre avec ce somptueux ensemble de 3 tableaux muraux assortis. Panneau central octogonal orné d'un feuillage doré et argenté texturé avec perle décorative, entouré de deux panneaux latéraux aux ondes célestes fluides. Impression haute définition sur support rigide haut de gamme, encadrement bordure or prestige. Installation facile et rendu ultra-chic garanti à Bamako.",
            "features": [
                "Composition : Ensemble triptyque complet 3 panneaux décoratifs",
                "Panneau central : Format octogonal relief avec anneau et perle",
                "Motifs : Feuillage d'or et argent, branches dorées et ondes artistiques lumineuses",
                "Finition : Bordures or métallisé luxe et verre synthétique brillant facile à nettoyer",
                "Usage : Idéal au-dessus d'un meuble TV, d'un canapé ou d'une console d'entrée",
                "Livraison express et soignée partout à Bamako par Onizuka Shop"
            ],
            "is_featured": True,
            "images": ["media_1795872756076_da371166.jpg"]
        },
        {
            "sku": "TAB-3P-ABSTRAIT-OR-02",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Art Abstrait Cercles Dorés & Marbrés",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque d'art moderne abstrait géométrique 3 pièces, disques marbrés or et bronze sur fond crème chaleureux.",
            "description": "Ce triptyque abstrait moderne apporte une touche contemporaine digne des plus grands hôtels de luxe. Il combine harmonieusement des formes géométriques circulaires avec textures marbre, feuille d'or texturée et nuances terre de sienne sur fond écru crème. Parfait pour les intérieurs modernes et épurés.",
            "features": [
                "Composition : 3 panneaux muraux harmonisés",
                "Style : Art abstrait contemporain minimaliste & géométrique",
                "Coloris : Or brossé, marron moka, gris perle et blanc marbré",
                "Encadrement : Cadre fin aluminium finition dorée dorée prestige",
                "Résistance : Anti-poussière, lavable au chiffon doux",
                "Service : Livraison sécurisée à domicile à Bamako"
            ],
            "is_featured": False,
            "images": ["media_1795872761619_94b45ff3.jpg"]
        },
        {
            "sku": "TAB-3P-SPIRALE-TURQUOISE-03",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Spirale Contemporaine Turquoise & Sphère Cyan",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Ensemble 3 tableaux design contemporain avec vortex 3D texturé turquoise et sphère cyan flottante.",
            "description": "Apportez fraîcheur et modernité à votre intérieur avec ce magnifique triptyque contemporain. Le panneau central octogonal dévoile une spirale tourbillonnante en relief 3D aux teintes turquoise et blanc nacre, complété par deux panneaux latéraux épurés mettant en scène une sphère cyan et une coupelle arquée.",
            "features": [
                "Composition : Triptyque 3 pièces design dynamique",
                "Éléments visuels : Spirale sculptée 3D nacre et turquoise, sphère cyan satinée",
                "Encadrement : Bordure dorée haut de gamme résistante",
                "Ambiance : Design zen, moderne et sophistiqué",
                "Livraison : Disponible immédiatement en stock à Bamako chez Onizuka Shop"
            ],
            "is_featured": False,
            "images": ["media_1795872768143_66fd1855.jpg"]
        },
        {
            "sku": "TAB-3P-CALLIGRAPHIE-MARBRE-04",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Calligraphie Islamique Dorée sur Marbre Crème",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque d'art spirituel islamique calligraphie dorée en médaillons royaux sur texture marbre blanc et or.",
            "description": "Un chef-d'œuvre de spiritualité et d'élégance pour votre foyer. Cet ensemble de 3 tableaux met à l'honneur les inscriptions sacrées dans de somptueux médaillons circulaires arabesques ornementés d'or. Le panneau central hexagonal abrite une calligraphie circulaire majestueuse, encadrée par deux médaillons d'or sur fond de marbre impérial.",
            "features": [
                "Composition : Triptyque complet 3 tableaux spirituels",
                "Calligraphie : Inscriptions coraniques sacrées calligraphiées à la feuille d'or",
                "Arrière-plan : Texture marbre naturel veiné blanc et crème avec arabesques dorées",
                "Format : Panneau central hexagonal + 2 panneaux latéraux panoramiques",
                "Bénédiction & Prestige : Idéal pour salon familial, entrée ou salle de prière",
                "Livraison rapide et soignée à Bamako"
            ],
            "is_featured": True,
            "images": ["media_1795872778203_b1b308c3.jpg"]
        },
        {
            "sku": "TAB-3P-FLEURS-GINKGO-05",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Fleurs d'Or & Feuilles de Ginkgo Lumineuses",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque luxe floral doré, fleurs sculptées, feuilles de ginkgo or et perles suspendues sur fond éclatant.",
            "description": "Inspiré de la noblesse de la nature, ce triptyque mural met en valeur des fleurs sculptées en or étincelant et les emblématiques feuilles de ginkgo biloba, symbole de longévité et de prospérité. Les finitions or chaud et les éléments suspendus créent une atmosphère chaleureuse et lumineuse dans votre pièce.",
            "features": [
                "Composition : 3 panneaux décoratifs d'inspiration florale noble",
                "Motifs : Fleurs épanouies d'or, feuilles de ginkgo or et turquoise, sphère ambrée",
                "Panneau central : Format octogonal encadré d'or avec reliefs fins",
                "Finition : Rendu ultra-lumineux et résistant aux reflets",
                "Qualité Onizuka Shop : Prêt à accrocher au mur avec fixations incluses"
            ],
            "is_featured": False,
            "images": ["media_1795872784150_7fa88044.jpg"]
        },
        {
            "sku": "TAB-3P-LOTUS-BLEU-06",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Fleur de Lotus Céleste & Rosée Nacrée",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque floral contemporain avec majestueuse fleur de lotus bleu azur, pistil ambré et gouttes de rosée.",
            "description": "Une œuvre murale d'une délicatesse exceptionnelle. Au centre, une spectaculaire fleur de lotus en éclosion aux pétales nacre et bleu ciel poudré, parsemée de micro-gouttes de rosée scintillantes et ornée d'un cœur orangé flamboyant. Les panneaux latéraux apportent un équilibre géométrique moderne avec nuances bleu nuit et beige.",
            "features": [
                "Composition : Triptyque 3 pièces grand format",
                "Pièce maîtresse : Fleur de lotus blanche et bleu azur avec pistil or et effet gouttelettes d'eau",
                "Cadre : Profilé métallique doré fin de haute précision",
                "Ambiance : Douceur, apaisement et raffinement pour salon ou chambre parentale",
                "Livraison express à domicile à Bamako"
            ],
            "is_featured": False,
            "images": ["media_1795872789926_426499d8.jpg"]
        },
        {
            "sku": "TAB-3P-CALLIGRAPHIE-NOIR-OR-07",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Calligraphie Islamique Royale Noir & Or",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque islamique majestueux Allah & Muhammad, calligraphie circulaire or et argent sur fond noir texturé.",
            "description": "D'une puissance visuelle remarquable, ce triptyque de calligraphie islamique associe le prestige de l'or brossé à la profondeur d'un fond marbré noir et or impérial. Au centre, l'Ayat sacré en médaillon calligraphique circulaire orné d'argent et d'or, entouré des médaillons saints Allah et Muhammad.",
            "features": [
                "Composition : 3 panneaux triptyque royaux",
                "Calligraphies : Allah (SWT), Muhammad (SAW) et médaillon coranique central",
                "Finitions : Or relief, argent métallique et texture marbre noir marquina",
                "Rendu : Élégance suprême et solennité pour votre salon ou bureau",
                "Garantie : Couleurs inaltérables et protection anti-UV"
            ],
            "is_featured": True,
            "images": ["media_1795872795909_03fd24f4.jpg"]
        },
        {
            "sku": "TAB-3P-MAGNOLIA-OR-08",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Nénuphars & Magnolias d'Or Rayonnants",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque floral 3 pièces magnolias épanouis aux dégradés or et blanc sur fond bleu canard royal.",
            "description": "Laissez entrer la lumière et le luxe dans votre maison avec ce triptyque de magnolias dorés. Les fleurs géantes aux pétales généreux offrent un saisissant dégradé du blanc immaculé vers un jaune d'or chaleureux, sublimé par un fond bleu ciel et canard contrasté.",
            "features": [
                "Composition : 3 panneaux avec pièce centrale hexagonale surélevée",
                "Motif : Fleurs de magnolias impériales aux dégradés or et nacrés",
                "Contraste : Fond bleu canard et ciel lumineux rehaussé de bordures or",
                "Parfait pour : Au-dessus d'une commode, d'un canapé ou dans une salle de réception",
                "Disponible chez Onizuka Shop avec livraison à Bamako"
            ],
            "is_featured": False,
            "images": ["media_1795872802091_e5a33a72.jpg"]
        },
        {
            "sku": "TAB-3P-FLEURS-3D-RUBAN-09",
            "name": "Tableau Décoratif Mural Triptyque 3 Pièces Fleurs d'Or Sculptées 3D & Ruban Satiné",
            "price": 35000,
            "category": cat_deco,
            "brand": b_onizuka_deco,
            "short_description": "Triptyque moderne 3 pièces avec fleurs dorées en relief 3D, galets texturés bleu nuit et ruban d'or ondulant.",
            "description": "Une composition d'une finesse artistique rare. Ce triptyque met en scène trois fleurs dorées sculptées en relief 3D disposées sur des galets bleu nuit texturés, reliées par un ruban fluide ondulant blanc et or. Le panneau central circulaire capte instantanément le regard.",
            "features": [
                "Composition : Triptyque moderne 3 panneaux (central circulaire + 2 latéraux arqués)",
                "Éléments artistiques : Fleurs d'or 3D en relief sculpté, ruban satiné ondulé",
                "Arrière-plan : Teintes gris perle et bleu nuit apaisantes avec reflets dorés",
                "Cadre : Profil doré haute qualité avec verre de protection",
                "Installation facile et livraison à Bamako"
            ],
            "is_featured": False,
            "images": ["media_1795872808509_24cb39cc.jpg"]
        }
    ]
    for tab in tableaux:
        create_product(tab, tab.get('images'))

    # --- 3. ENCEINTES PORTABLES JBL ---
    # 3.1 JBL Flip 7 (98 000 FCFA)
    create_product({
        "sku": "JBL-FLIP-7",
        "name": "Enceinte Portable Bluetooth JBL Flip 7 Pro Sound Originale (16H d'Autonomie)",
        "price": 98000,
        "old_price": 115000,
        "category": cat_audio,
        "brand": b_jbl,
        "short_description": "Enceinte étanche JBL Flip 7 nouvelle génération, Bluetooth 5.4, 16h de batterie, son puissant Pro Sound, coloris disponibles.",
        "description": "La référence mondiale des enceintes nomades passe à la vitesse supérieure avec la JBL Flip 7 ! Équipée du son JBL Original Pro Sound avec basses percutantes, d'une autonomie longue durée de 16 heures et de la toute dernière puce Bluetooth v5.4 pour une connexion ultra-stable sans latence. Entièrement étanche à l'eau et à la poussière (norme IP67), elle vous accompagne partout à Bamako, à la piscine, au salon ou en voyage. Disponible en plusieurs coloris tendance (Camouflage militaire, Blanc pur, Rouge vif).",
        "features": [
            "Marque : JBL by HARMAN (Originale certifiée)",
            "Modèle : JBL Flip 7 Pro Sound",
            "Connectivité : Bluetooth 5.4 ultra-rapide et stable",
            "Autonomie : Jusqu'à 16 heures de musique non-stop",
            "Étanchéité : Résistante à l'eau et aux éclaboussures IP67",
            "Coloris en stock : Camouflage, Blanc, Rouge",
            "Recharge : USB-C Charge rapide",
            "Livraison rapide partout à Bamako par Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795872828262_02010266.jpg"])

    # 3.2 JBL Charge 5 (110 000 FCFA)
    create_product({
        "sku": "JBL-CHARGE-5",
        "name": "Enceinte Portable Bluetooth JBL Charge 5 avec Powerbank Intégrée (20H d'Autonomie)",
        "price": 110000,
        "old_price": 130000,
        "category": cat_audio,
        "brand": b_jbl,
        "short_description": "Enceinte Bluetooth JBL Charge 5 étanche, 20h d'autonomie, fonction Powerbank pour recharger vos smartphones, son puissant.",
        "description": "Faites la fête sans jamais vous arrêter avec l'enceinte portable JBL Charge 5. Elle délivre un son JBL Original Pro incroyablement puissant grâce à son haut-parleur de graves longue portée, son haut-parleur haute fréquence séparé et ses deux radiateurs de basses passifs JBL. Offrant jusqu'à 20 heures d'autonomie et équipée d'une batterie externe (powerbank) USB intégrée, elle vous permet de recharger votre téléphone tout en écoutant votre musique. Robuste, étanche à l'eau et à la poussière. Disponibilité en plusieurs finitions (Camouflage, Rouge, Rose poudré).",
        "features": [
            "Marque : JBL by HARMAN",
            "Modèle : JBL Charge 5",
            "Autonomie : 20 heures d'écoute continue",
            "Fonction Powerbank : Rechargez vos téléphones directement sur l'enceinte via USB",
            "Étanchéité : Certification IP67 résistant à l'eau et à la poussière",
            "Bluetooth : Bluetooth v5.1 / v5.3 haute fidélité",
            "Basses : Deux radiateurs passifs pour des basses profondes et percutantes",
            "Coloris disponibles : Camouflage, Rouge vif, Rose poudré / Coral",
            "Livraison express à domicile à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795872861409_2bf50978.jpg", "media_1795872898940_a9afdc08.jpg"])

    # 3.3 JBL Xtreme 4 (215 000 FCFA)
    create_product({
        "sku": "JBL-XTREME-4",
        "name": "Enceinte Portable Bluetooth Géante JBL Xtreme 4 Pro Sound (24H d'Autonomie)",
        "price": 215000,
        "old_price": 245000,
        "category": cat_audio,
        "brand": b_jbl,
        "short_description": "Enceinte nomade colossale JBL Xtreme 4, son massif de festival, 24 heures de batterie, étanche IP67 avec sangle de transport.",
        "description": "Entrez dans une autre dimension sonore avec la monumentale JBL Xtreme 4. Conçue pour faire vibrer les grands espaces intérieurs comme extérieurs, elle intègre deux woofers massifs et deux tweeters dynamiques délivrant un volume sonore prodigieux et des basses ultra-profondes. Sa batterie colossale assure jusqu'à 24 heures d'autonomie avec fonction charge rapide et powerbank intégrée. Livrée avec sa sangle d'épaule confortable, disponible en Bleu Nuit et Noir Profond.",
        "features": [
            "Marque : JBL by HARMAN",
            "Modèle : JBL Xtreme 4 Pro Sound",
            "Puissance : Son massif haute fidélité pour fêtes, salons et extérieurs",
            "Autonomie : 24 heures d'autonomie extrême avec fonction Powerbank",
            "Connectivité : Bluetooth 5.3 nouvelle génération",
            "Protection : Étanche IP67 résistante aux immersions et au sable",
            "Transport : Sangle de transport robuste et décapsuleur intégré",
            "Coloris : Bleu Nuit et Noir",
            "Garantie Onizuka Shop avec livraison offerte à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795872916838_e16854ff.jpg"])

    # --- 4. RÉFRIGÉRATEURS COMBINÉS & BAR ---
    # 4.1 Pearl Combiné Noir Vitré PF-370 (290 000 FCFA)
    create_product({
        "sku": "PEARL-COMB-PF370-NOIR",
        "name": "Réfrigérateur Combiné Pearl 370L Noir Vitré PF-370 avec Distributeur d'Eau",
        "price": 290000,
        "old_price": 320000,
        "category": cat_refrig,
        "brand": b_pearl,
        "short_description": "Réfrigérateur combiné grande capacité 370L finition verre noir miroir avec fontaine à eau intégrée en façade.",
        "description": "L'alliance parfaite du grand luxe et de la performance moderne. Ce réfrigérateur combiné Pearl PF-370 arbore une magnifique façade en verre trempé noir miroir avec distributeur d'eau fraîche intégré sans raccordement nécessaire. Partie réfrigérateur spacieuse en haut avec clayettes en verre sécurit et bac à légumes Fresh Zone, partie congélateur 3 tiroirs en bas pour une congélation rapide et sans givre. Compresseur tropicalisé robuste spécialement adapté au climat de Bamako.",
        "features": [
            "Marque : Pearl Freshness Lives Here",
            "Modèle : PF-370 Noir Vitré",
            "Volume total : 370 Litres grand format familial",
            "Distributeur d'eau : Fontaine à eau fraîche intégrée en façade (Water Dispenser)",
            "Façade : Finition verre trempé noir miroir anti-rayures ultra-facile à nettoyer",
            "Congélateur : En bas avec 3 grands tiroirs transparents coulissants",
            "Technologie : Froid ventilé Fresh Zone et compresseur tropicalisé basse consommation A+",
            "Livraison et installation offertes à Bamako par Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795872982126_ddccf822.jpg", "media_1795873001907_eb67da34.jpg"])

    # 4.2 Hisense Combiné Inox Distributeur (265 000 FCFA)
    create_product({
        "sku": "HISENSE-COMB-DISTRIB-INOX",
        "name": "Réfrigérateur Combiné Hisense Inox Silver avec Distributeur d'Eau Fraîche",
        "price": 265000,
        "old_price": 295000,
        "category": cat_refrig,
        "brand": b_hisense,
        "short_description": "Réfrigérateur combiné Hisense Silver Inox avec fontaine à eau intégrée, congélateur 3 tiroirs et clayettes réglables.",
        "description": "Profitez de l'excellence et de la fiabilité mondiale Hisense. Ce combiné réfrigérateur-congélateur en finition acier inoxydable Silver dispose d'un distributeur d'eau fraîche en façade pour vous désaltérer à tout moment sans ouvrir la porte. Son intérieur modulable offre 4 niveaux de rangement en verre renforcé, un bac fraîcheur pour fruits et légumes, et un congélateur inférieur à 3 tiroirs coulissants pour stocker viandes et poissons en toute tranquillité.",
        "features": [
            "Marque : Hisense",
            "Configuration : Combiné 2 portes (Réfrigérateur haut + Congélateur bas)",
            "Distributeur : Fontaine à eau fraîche intégrée en façade",
            "Finition : Acier brossé Inox Silver anti-traces de doigts",
            "Aménagement : 4 clayettes en verre trempé, balconnets de porte et bac à légumes",
            "Congélation : 3 tiroirs transparents à congélation rapide",
            "Compresseur : Silencieux, économique et tropicalisé haute résistance",
            "Livraison et mise en service incluses à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795873033468_5a56f366.jpg", "media_1795873046584_46f52187.jpg"])

    # 4.3 Roch 200 Litres Combiné 200DB (179 000 FCFA)
    create_product({
        "sku": "ROCH-COMB-200DB",
        "name": "Réfrigérateur Combiné Roch 200 Litres Nature Fresh RFR-200DB Gris Titane",
        "price": 179000,
        "old_price": 199000,
        "category": cat_refrig,
        "brand": b_roch,
        "short_description": "Réfrigérateur combiné Roch 200L, technologie Nature Fresh, compresseur tropicalisé fiable avec serrure à clé.",
        "description": "Le réfrigérateur combiné idéal pour les familles cherchant fiabilité, gain de place et grande efficacité énergétique. Le Roch RFR-200DB Nature Fresh propose un compartiment réfrigérateur supérieur clair et bien agencé avec clayettes réglables et éclairage LED, complété par un compartiment congélateur inférieur à 3 bacs étanches. Équipé d'une serrure à clé intégrée pour verrouiller vos denrées en toute sécurité.",
        "features": [
            "Marque : Roch Smart Refrigerator (Garantie 12 Mois)",
            "Modèle : 200DB Nature Fresh",
            "Capacité totale : 200 Litres",
            "Finition : Gris titane anthracite satiné premium",
            "Sécurité : Serrure à clé intégrée sur la porte congélateur",
            "Éclairage : Lumière intérieure LED claire et basse consommation",
            "Régulateur de tension : Compatible avec les variations de tension locales",
            "Livraison rapide et sécurisée à Bamako"
        ],
        "is_featured": False,
    }, ["media_1795873061158_a68d9176.jpg", "media_1795873068398_6a9aaa6a.jpg"])

    # 4.4 Vodacom Bar 90L Inox (99 000 FCFA)
    create_product({
        "sku": "VODACOM-BAR-90L",
        "name": "Réfrigérateur Bar Double Porte Vodacom 90 Litres VRF-85T Inox avec Serrure",
        "price": 99000,
        "old_price": 115000,
        "category": cat_refrig,
        "brand": b_vodacom,
        "short_description": "Réfrigérateur bar compact double porte 90L avec vrai congélateur séparé, finition inox et serrure à clé.",
        "description": "Le réfrigérateur bar le plus performant de sa catégorie ! Contrairement aux mini-bars classiques à une seule porte, ce modèle Vodacom VRF-85T dispose d'une VRAIE double porte : un compartiment congélateur supérieur indépendant (25L) pour fabriquer des glaçons et congeler rapidement, et un compartiment réfrigérateur inférieur (65L) avec bac à légumes et serrure à clé. Idéal pour chambres, bureaux, studios ou commerces à Bamako.",
        "features": [
            "Marque : Vodacom Electronics (Garantie 12 Mois)",
            "Modèle : VRF-85T / VRF-95T Double Porte",
            "Volume total : 90 Litres (dont 25L congélateur séparé)",
            "Double porte : Congélateur haut indépendant + Réfrigérateur bas",
            "Finition : Inox Silver élégant avec serrure à clé sur la porte basse",
            "Consommation : Classe énergétique A éco-responsable (Faible bruit 38dB)",
            "Format : Compact, idéal pour chambre, salon d'attente ou bureau",
            "Livraison express à domicile à Bamako par Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795873088045_b9bd9b91.jpg", "media_1795873094198_ea7d4d0a.jpg"])

    # --- 5. COFFRES-FORTS HAUTE SÉCURITÉ ---
    # 5.1 Coffre 105 kg (256 000 FCFA)
    create_product({
        "sku": "COFFRE-FORT-105KG",
        "name": "Coffre-Fort Blindé Ignifuge Lourd 105 kg Double Serrure à Clés Sécurisées",
        "price": 256000,
        "old_price": 290000,
        "category": cat_coffres,
        "brand": b_safe,
        "short_description": "Coffre-fort blindé professionnel 105 kg, ignifuge résistant au feu, double serrure haute sécurité à clé.",
        "description": "La protection maximale pour vos fonds, documents confidentiels, titres de propriété et objets de valeur. Pesant 105 kg, ce coffre blindé lourd décourage toute tentative d'arrachement ou de transport illicite. Il est conçu avec des parois en acier multicouche et un blindage ignifuge certifié résistant aux incendies (Fire Resistant Safe). Équipé d'un système de fermeture à double serrure mécanique haute précision avec deux clés distinctes indispensables pour l'ouverture.",
        "features": [
            "Poids : 105 kg lourd inamovible",
            "Sécurité : Double serrure à clé crantée haute sécurité (Double Key Lock)",
            "Protection incendie : Parois ignifuges certifiées Fire Resistant Safe",
            "Charnières : Charnières massives extérieures en acier trempé anti-sciage",
            "Mobilité : Roulettes renforcées intégrées à la base pour faciliter l'installation",
            "Usage : Idéal pour commerces, entreprises, agences et domiciles sécurisés",
            "Livraison et déchargement sécurisés à Bamako par l'équipe Onizuka Shop"
        ],
        "is_featured": True,
    }, ["media_1795873119556_a53147bd.jpg"])

    # 5.2 Coffre 75 kg Colonne Digitale (310 000 FCFA)
    create_product({
        "sku": "COFFRE-FORT-75KG-DIGITALE",
        "name": "Coffre-Fort Colonne Haute Sécurité 75 kg Double Serrure Digitale & Clé d'Urgence",
        "price": 310000,
        "old_price": 350000,
        "category": cat_coffres,
        "brand": b_safe,
        "short_description": "Coffre-fort format armoire colonne 75 kg avec panneau digital tactile, poignée rotative et clé de secours.",
        "description": "Le summum de la sécurité moderne pour bureaux de direction et résidences de standing. D'un poids solide de 75 kg avec un format colonne élancé, ce coffre-fort intègre une double serrure électronique digitale tactile XinFort combinée à une clé maîtresse. En cas d'oubli de code ou de pile déchargée, un jeu de clés d'urgence permet une ouverture mécanique instantanée. Finitions de prestige disponibles en Blanc Crème Métallisé et Noir Granité Martelé.",
        "features": [
            "Poids : 75 kg haute stabilité",
            "Verrouillage : Double serrure digitale électronique + Serrure à clé mécanique",
            "Contrôle d'accès : Clavier numérique programmable et alerte sonore anti-effraction",
            "Urgence : Clé de secours extérieure en cas d'oubli de code",
            "Aménagement intérieur : Étagères intérieures spacieuses pour classeurs et dossiers A4",
            "Coloris au choix : Noir martelé ou Blanc crème élégant",
            "Livraison discrète et installation sécurisée à Bamako"
        ],
        "is_featured": True,
    }, ["media_1795873145370_c327ece5.jpg", "media_1795873150811_3f2e1697.jpg"])

    # 5.3 Coffre 55 kg (140 000 FCFA)
    create_product({
        "sku": "COFFRE-FORT-55KG",
        "name": "Coffre-Fort Ignifuge Renforcé 55 kg Double Serrure Mécanique à Clés",
        "price": 140000,
        "old_price": 165000,
        "category": cat_coffres,
        "brand": b_safe,
        "short_description": "Coffre-fort robuste 55 kg ignifuge, double serrure à clés indépendantes, charnières renforcées en acier.",
        "description": "Un excellent compromis entre compacité et sécurité maximale. Ce coffre de 55 kg bénéficie d'une conception ignifuge multicouche anti-feu (Be Free from Fire !) et d'une double serrure mécanique sans électronique : aucune pile à changer, une fiabilité infaillible à vie. Équipé de pênes en acier massif pour bloquer hermétiquement la porte.",
        "features": [
            "Poids : 55 kg massif",
            "Fermeture : Double serrure mécanique haute précision à 2 clés distinctes",
            "Protection thermique : Norme ignifuge de résistance aux hautes températures",
            "Construction : Acier lourd anti-perçage et pênes de verrouillage épais",
            "Usage : Domicile, caisse de boutique, comptabilité de bureau",
            "Livraison rapide à Bamako par Onizuka Shop"
        ],
        "is_featured": False,
    }, ["media_1795873125522_7c9380eb.jpg"])

    # 5.4 Coffre 30 kg Double Serrure Digitale (205 000 FCFA)
    create_product({
        "sku": "COFFRE-FORT-30KG-DIGITALE",
        "name": "Coffre-Fort Blindé 30 kg Double Serrure Digitale Tactile & Clé XinFort",
        "price": 205000,
        "old_price": 235000,
        "category": cat_coffres,
        "brand": b_safe,
        "short_description": "Coffre-fort moderne 30 kg double serrure digitale électronique tactile, alarme anti-choc et clé de secours.",
        "description": "Ce coffre-fort nouvelle génération de 30 kg réunit design contemporain et technologie de pointe. Il intègre la console digitale XinFort avec écran tactile rétroéclairé, ouverture par code confidentiel, et double sécurité par clé. Parfaitement adapté pour être fixé au sol ou au mur grâce à ses points d'ancrage renforcés.",
        "features": [
            "Poids : 30 kg idéal pour fixation meuble, sol ou mur",
            "Double serrure : Clavier électronique digital tactile + Serrure à clé protégée",
            "Sécurité électronique : Verrouillage automatique après 3 codes erronés et alarme",
            "Finition : Laquage argenté champagne martelé grand luxe",
            "Fixation : Trous de fixation pré-percés à l'arrière et au sol",
            "Livraison à domicile à Bamako"
        ],
        "is_featured": False,
    }, ["media_1795873132046_ffafe70b.jpg"])

    # 5.5 Coffre 4 kg Compact Électronique (65 000 FCFA)
    create_product({
        "sku": "COFFRE-FORT-4KG-DIGITAL",
        "name": "Coffre-Fort Électronique Compact 4 kg Clavier Numérique & Clés d'Urgence",
        "price": 65000,
        "old_price": 79000,
        "category": cat_coffres,
        "brand": b_safe,
        "short_description": "Coffre-fort compact hôtel & maison 4 kg, ouverture par code digital 3 à 8 chiffres + 2 clés d'urgence manuelles.",
        "description": "Le coffre-fort compact indispensable pour protéger rapidement passeports, bijoux, argent liquide et cartes bancaires. Doté d'un boîtier en acier robuste avec finition noire mate, il se verrouille par code PIN électronique personnalisable de 3 à 8 chiffres. Deux clés de secours tubulaires sont fournies pour l'ouverture manuelle d'urgence. Facile à encastrer dans une armoire ou à fixer sur une étagère.",
        "features": [
            "Poids : 4 kg ultra-maniable et compact",
            "Verrouillage : Clavier numérique avec voyants LED indicateurs (Vert, Rouge, Jaune)",
            "Pênes : 2 gros pênes en acier massif motorisés",
            "Clés d'urgence : 2 clés fournies en cas d'oubli de code ou batterie faible",
            "Fixation : Pré-percé avec chevilles métalliques incluses",
            "Usage : Idéal chambre, hôtel, placard ou tiroir de bureau",
            "Disponible immédiatement en stock à Bamako chez Onizuka Shop"
        ],
        "is_featured": False,
    }, ["media_1795873138429_541c9a98.jpg"])

    print("\n🎉 === IMPORTATION DU LOT 3 TERMINÉE AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    run_import()
