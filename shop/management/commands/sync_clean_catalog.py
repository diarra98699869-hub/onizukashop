from django.core.management.base import BaseCommand
from django.core.management import call_command
from shop.models import Product, Category, Brand

class Command(BaseCommand):
    help = "Nettoie tous les anciens produits de démonstration et charge le vrai catalogue showroom Onizuka Shop (35 références réelles)"

    def handle(self, *args, **options):
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
