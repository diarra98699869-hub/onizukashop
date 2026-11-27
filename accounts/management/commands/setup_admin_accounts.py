from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

DEFAULT_ACCOUNTS = [
    {
        'username': 'alasko_ff',
        'email': 'alasko6e6ui3e@gmail.com',
        'password': 'www.Diarra9869.com',
        'first_name': 'Super',
        'last_name': 'Admin IT',
        'is_staff': True,
        'is_superuser': True,
        'phone': '+223 92 67 37 99',
    },
    {
        'username': 'admin_onizouka',
        'email': 'direction@onizoukashop.com',
        'password': 'onizouka123',
        'first_name': 'Direction',
        'last_name': 'Onizouka',
        'is_staff': True,
        'is_superuser': False,
        'phone': '+223 92 67 37 99',
    },
    {
        'username': 'client',
        'email': 'client@onizoukashop.com',
        'password': 'client123',
        'first_name': 'Client',
        'last_name': 'Acheteur',
        'is_staff': False,
        'is_superuser': False,
        'phone': '+223 70 00 00 00',
    },
]

class Command(BaseCommand):
    help = "Initialise ou réinitialise les 3 comptes officiels d'Onizouka Shop (IT, Direction, Client Test)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> Configuration des comptes système officiels..."))
        for acc in DEFAULT_ACCOUNTS:
            user, created = User.objects.get_or_create(username=acc['username'])
            user.email = acc['email']
            user.first_name = acc['first_name']
            user.last_name = acc['last_name']
            user.is_staff = acc['is_staff']
            user.is_superuser = acc['is_superuser']
            user.is_active = True
            user.set_password(acc['password'])
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            if acc.get('phone'):
                profile.phone = acc['phone']
                profile.save()

            action = "Créé" if created else "Mis à jour"
            role = "Super-Admin IT" if user.is_superuser else ("Direction (Staff)" if user.is_staff else "Client")
            self.stdout.write(self.style.SUCCESS(f"  [OK] Compte {acc['username']} ({role}) : {action}"))

        self.stdout.write(self.style.SUCCESS(">>> 100% des comptes officiels sont configurés et opérationnels !"))
