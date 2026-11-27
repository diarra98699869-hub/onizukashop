"""
Liaison directe et universelle (Production & Local) des images WebP des congélateurs coffres.
Ce script ne requiert AUCUN fichier temporaire ou chemin Windows:
Il utilise directement les images .webp committées dans media/products/congelateurs_coffres/
et les associe dans ProductImage de manière idempotente.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
import django
django.setup()

from django.db import transaction
from shop.models import Product, ProductImage

MEDIA_ROOT = BASE_DIR / 'media'

PRODUCT_IMAGES_MAPPING = {
    # 1. Fizzen (7 modèles: ONZ-FZ-CH-*)
    'ONZ-FZ-CH-110L': [
        ('products/congelateurs_coffres/fizzen_coffre_110l_ferme.webp', True, 'Vue fermée'),
        ('products/congelateurs_coffres/fizzen_coffre_110l_ouvert.webp', False, 'Vue ouverte avec vitres coulissantes'),
    ],
    'ONZ-FZ-CH-160L': [
        ('products/congelateurs_coffres/fizzen_coffre_160l_ferme.webp', True, 'Vue fermée'),
        ('products/congelateurs_coffres/fizzen_coffre_160l_ouvert.webp', False, 'Vue ouverte avec panier'),
    ],
    'ONZ-FZ-CH-210L': [
        ('products/congelateurs_coffres/fizzen_coffre_210l_ferme.webp', True, 'Vue fermée'),
        ('products/congelateurs_coffres/fizzen_coffre_210l_ouvert.webp', False, 'Vue intérieure'),
    ],
    'ONZ-FZ-CH-270L': [
        ('products/congelateurs_coffres/fizzen_coffre_270l_ferme.webp', True, 'Vue fermée'),
        ('products/congelateurs_coffres/fizzen_coffre_270l_ouvert.webp', False, 'Vue intérieure cuve'),
    ],
    'ONZ-FZ-CH-350L': [
        ('products/congelateurs_coffres/fizzen_coffre_350l_ferme.webp', True, 'Vue fermée 2 battants'),
        ('products/congelateurs_coffres/fizzen_coffre_350l_ouvert.webp', False, 'Vue intérieure spacieuse'),
    ],
    'ONZ-FZ-CH-430L': [
        ('products/congelateurs_coffres/fizzen_coffre_430l_ferme.webp', True, 'Vue fermée 2 battants'),
        ('products/congelateurs_coffres/fizzen_coffre_430l_ouvert.webp', False, 'Vue intérieure grande capacité'),
    ],
    'ONZ-FZ-CH-550L': [
        ('products/congelateurs_coffres/fizzen_coffre_550l_ferme.webp', True, 'Vue fermée 2 battants PRO'),
        ('products/congelateurs_coffres/fizzen_coffre_550l_ouvert.webp', False, 'Vue intérieure commerciale'),
    ],
    # 2. Roch (2 modèles)
    'ONZ-ROCH-CH-316L': [
        ('products/congelateurs_coffres/roch_coffre_316l_ferme.webp', True, 'Vue extérieure'),
        ('products/congelateurs_coffres/roch_coffre_316l_ouvert.webp', False, 'Vue intérieure vitres coulissantes'),
    ],
    'ONZ-ROCH-CH-550L': [
        ('products/congelateurs_coffres/roch_coffre_550l_ferme.webp', True, 'Vue extérieure 2 battants'),
        ('products/congelateurs_coffres/roch_coffre_550l_ouvert.webp', False, 'Vue ouverte grand volume'),
    ],
    # 3. Pearl (1 modèle)
    'ONZ-PEARL-CH-375L': [
        ('products/congelateurs_coffres/pearl_coffre_375l_ferme.webp', True, 'Vue extérieure fermée'),
        ('products/congelateurs_coffres/pearl_coffre_375l_ouvert.webp', False, 'Vue ouverte 2 battants'),
        ('products/congelateurs_coffres/pearl_coffre_375l_interieur_badge.webp', False, 'Détail vitres et badge'),
    ],
    # 4. TMT (2 modèles)
    'ONZ-TMT-CH-200L': [
        ('products/congelateurs_coffres/tmt_coffre_200l_ferme.webp', True, 'Vue extérieure'),
        ('products/congelateurs_coffres/tmt_coffre_200l_ouvert.webp', False, 'Vue intérieure vitres coulissantes'),
    ],
    'ONZ-TMT-CH-288L': [
        ('products/congelateurs_coffres/tmt_coffre_288l_ferme.webp', True, 'Vue extérieure'),
        ('products/congelateurs_coffres/tmt_coffre_288l_ouvert.webp', False, 'Vue intérieure vitres coulissantes'),
    ],
    # 5. Sharp (2 modèles)
    'ONZ-SHP-CH-450L': [
        ('products/congelateurs_coffres/sharp_coffre_450l_ref580.webp', True, 'Vue officielle Sharp Réf 580'),
    ],
    'ONZ-SHP-CH-520L': [
        ('products/congelateurs_coffres/sharp_coffre_520l_ref660_ferme.webp', True, 'Vue extérieure 2 battants Réf 660'),
        ('products/congelateurs_coffres/sharp_coffre_520l_ref660_ouvert.webp', False, 'Vue intérieure grand volume'),
    ],
    # 6. Telimani (2 modèles)
    'ONZ-TEL-CH-212L': [
        ('products/congelateurs_coffres/telimani_coffre_212l_ferme.webp', True, 'Vue extérieure'),
        ('products/congelateurs_coffres/telimani_coffre_212l_ouvert.webp', False, 'Vue ouverte avec vitres'),
    ],
    'ONZ-TEL-CH-650L': [
        ('products/congelateurs_coffres/telimani_coffre_650l_ferme.webp', True, 'Vue extérieure fermée 2 battants'),
        ('products/congelateurs_coffres/telimani_coffre_650l_ouvert.webp', False, 'Vue ouverte professionnelle'),
    ],
    # 7. NAFA (3 modèles)
    'ONZ-NAFA-CH-148L': [
        ('products/congelateurs_coffres/nafa_coffre_148l_bd198.webp', True, 'Vue compacte NAFA 148L BD-198'),
    ],
    'ONZ-NAFA-CH-248L': [
        ('products/congelateurs_coffres/nafa_coffre_248l_bd298.webp', True, 'Vue intermédiaire NAFA 248L BD-298'),
    ],
    'ONZ-NAFA-CH-348L': [
        ('products/congelateurs_coffres/nafa_coffre_348l_bd398.webp', True, 'Vue grand modèle NAFA 348L BD-398'),
    ],
    # 8. LG (1 modèle)
    'ONZ-LG-CH-345L': [
        ('products/congelateurs_coffres/lg_coffre_345l_ferme.webp', True, 'Vue extérieure fermée officielle'),
        ('products/congelateurs_coffres/lg_coffre_345l_ouvert.webp', False, 'Vue intérieure avec panier et compartiment'),
        ('products/congelateurs_coffres/lg_coffre_345l_plaque_technique.webp', False, 'Plaque technique constructeur LG'),
    ],
    # 9. Nouveaux Congélateurs Coffres Ajoutés
    'ONZ-PEARL-CH-450L': [
        ('products/congelateurs_coffres/pearl_450_ferme.webp', True, 'Vue fermée 2 battants Pearl 450L'),
        ('products/congelateurs_coffres/pearl_450_ouvert.webp', False, 'Vue intérieure cuve spacieuse et vitres coulissantes'),
    ],
    'ONZ-SHP-CH-325L': [
        ('products/congelateurs_coffres/sharp_325_400xi.webp', True, 'Vue ouverte Sharp 325L 400XI avec vitres coulissantes'),
    ],
    'ONZ-ROCH-CH-450L': [
        ('products/congelateurs_coffres/roch_450_ruf450g_ouvert.webp', True, 'Vue 2 battants ouverts Roch 450L RUF-450G'),
        ('products/congelateurs_coffres/roch_450_rcf450g_plaque.webp', False, 'Plaque signalétique officielle Roch RCF-450-G'),
    ],
    'ONZ-ROCH-CH-200L': [
        ('products/congelateurs_coffres/roch_200_ruf250g_ferme.webp', True, 'Vue fermée Roch 200L RUF-250G gris foncé'),
        ('products/congelateurs_coffres/roch_200_ruf250g_ouvert.webp', False, 'Vue intérieure cuve et vitres de protection'),
    ],
    'ONZ-ETOILE-CH-650L': [
        ('products/congelateurs_coffres/etoile_650_xfl650.webp', True, 'Vue de face Étoile 650 Litres XFL-650 grand volume'),
    ],
    'ONZ-ETOILE-CH-750L': [
        ('products/congelateurs_coffres/etoile_750_xfl750.webp', True, 'Vue de face Étoile 750 Litres XFL-750 format géant'),
    ],
    'ONZ-PEARL-CH-251L': [
        ('products/congelateurs_coffres/pearl_251_pcf3160.webp', True, 'Vue ouverte Pearl 251L PCF-3160 avec vitres coulissantes'),
    ],
    'ONZ-PEARL-CH-299L': [
        ('products/congelateurs_coffres/pearl_299_pcf361.webp', True, 'Vue ouverte Pearl 299L PCF-361 avec vitres'),
    ],
    # 10. Vitrines Réfrigérées Roch
    'ONZ-VITR-ROCH-209L': [
        ('products/vitrines/roch_vitrine_209l_rsf260.webp', True, 'Vue vitrine réfrigérée Roch 209 Litres RSF-260 showroom'),
        ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
    ],
    'ONZ-VITR-ROCH-279L': [
        ('products/vitrines/roch_vitrine_279l_rsf350.webp', True, 'Vue vitrine réfrigérée Roch 279 Litres RSF-350 showroom'),
        ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
    ],
    'ONZ-VITR-ROCH-329L': [
        ('products/vitrines/roch_vitrine_329l_rsf410.webp', True, 'Vue vitrine réfrigérée Roch 329 Litres RSF-410'),
        ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Vue de la gamme vitrines Roch chez Onizouka Shop'),
    ],
    'ONZ-VITR-ROCH-550L': [
        ('products/vitrines/roch_vitrine_550l_rsf680_face.webp', True, 'Vue de face vitrine Roch 550L RSF-680 double battant'),
        ('products/vitrines/roch_vitrine_550l_rsf680_interieur.webp', False, 'Vue intérieure cuve et clayettes vitrine 550L'),
        ('products/vitrines/roch_vitrines_gamme_showroom.webp', False, 'Gamme complète de vitrines Roch Onizouka Shop'),
    ],
}

def link_images():
    print("=== LIAISON DES IMAGES DES CONGÉLATEURS COFFRES ===")
    total_linked = 0
    total_products = 0

    with transaction.atomic():
        for sku, images in PRODUCT_IMAGES_MAPPING.items():
            try:
                product = Product.objects.get(sku=sku)
            except Product.DoesNotExist:
                print(f"[MANQUANT] Produit non trouvé pour le SKU : {sku}")
                continue

            total_products += 1
            print(f"\nTraitement : {sku} ({product.name[:45]}...)")

            # Réinitialiser les anciennes images si nécessaire ou mettre à jour
            for rel_path, is_primary, alt_text in images:
                full_path = MEDIA_ROOT / rel_path
                if not full_path.exists():
                    print(f"  [ATTENTION] Fichier introuvable sur le disque : {full_path}")
                    continue

                img_obj, created = ProductImage.objects.update_or_create(
                    product=product,
                    image=rel_path,
                    defaults={
                        'is_primary': is_primary,
                        'alt_text': alt_text,
                    }
                )
                status = "Créée" if created else "Mise à jour"
                print(f"  -> Image {status} ({'Principale' if is_primary else 'Secondaire'}) : {rel_path}")
                total_linked += 1

    print(f"\n=== OPÉRATION TERMINÉE ===")
    print(f"Produits traités : {total_products}")
    print(f"Images associées : {total_linked}")

if __name__ == '__main__':
    link_images()
