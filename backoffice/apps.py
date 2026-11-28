from django.apps import AppConfig


class BackofficeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backoffice'
    verbose_name = 'Gestion Onizuka Shop'

    def ready(self):
        # Charge les signaux de surveillance anti-intrusion (échecs login, bruteforce)
        import onizouka.security_shield  # noqa: F401
