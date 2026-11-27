from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from shop.models import Product, Category, Brand

class Command(BaseCommand):
    help = "Nettoie tous les anciens produits de démonstration et charge le vrai catalogue showroom Onizuka Shop (35 références réelles)"

    def handle(self, *args, **options):
        # Mettre à jour .env avec les paramètres email si présent
        env_file = os.path.join(settings.BASE_DIR, '.env')
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'EMAIL_HOST_PASSWORD=' in content and 'shop20262027' not in content:
                    lines = content.splitlines()
                    new_lines = []
                    for line in lines:
                        if line.startswith('EMAIL_HOST_PASSWORD='):
                            new_lines.append('EMAIL_HOST_PASSWORD=shop20262027')
                        else:
                            new_lines.append(line)
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines) + '\n')
                    self.stdout.write(self.style.SUCCESS("  [OK] Mot de passe SMTP contact@onizukashop.com injecté dans .env"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  [WARN] Mise à jour .env sautée: {e}"))

        self.stdout.write(self.style.NOTICE(">>> Nettoyage des anciens produits fictifs..."))
        real_prefixes = ('ONZ-FZ-', 'ONZ-SAM-', 'ONZ-LG-', 'ONZ-EP-', 'ONZ-SHP-', 'ONZ-RCH-', 'ONZ-HYU-', 'ONZ-SHPINV-')

        to_delete = Product.objects.exclude(sku__startswith=real_prefixes[0])
        for prefix in real_prefixes[1:]:
            to_delete = to_delete.exclude(sku__startswith=prefix)

        nb_del = to_delete.count()
        to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"  [OK] {nb_del} anciens produits supprimés avec succès."))

        # Supprimer les anciennes catégories et marques vides
        Category.objects.filter(products__isnull=True).delete()
        Brand.objects.filter(products__isnull=True).delete()

        # Charger le vrai catalogue officiel
        self.stdout.write(self.style.NOTICE(">>> Chargement des 35 vrais produits réels et photos HD..."))
        call_command('loaddata', 'fixtures/catalog_data.json')

        # Synchroniser les comptes officiels
        self.stdout.write(self.style.NOTICE(">>> Synchronisation des comptes administrateurs officiels..."))
        call_command('setup_admin_accounts')

        total = Product.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f">>> CATALOGUE 100% PROPRE ET SYNCHRONISÉ ({total} produits réels au Grand Marché) !"))
