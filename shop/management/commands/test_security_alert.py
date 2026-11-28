"""
ONIZUKA SHOP - Commande Management : test_security_alert
Simule une tentative d'intrusion et envoie immédiatement un email d'alerte complet
à admin@danayaplus.com afin de valider la configuration SMTP en production.
"""
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from onizouka.security_shield import (
    SECURITY_ALERT_EMAIL,
    collect_forensic_summary,
    record_and_alert_intrusion,
)


class Command(BaseCommand):
    help = f"Envoie un email de test d'alerte anti-intrusion vers {SECURITY_ALERT_EMAIL}"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(f"Envoi d'une simulation d'alerte intrusion vers {SECURITY_ALERT_EMAIL}..."))

        rf = RequestFactory()
        fake_req = rf.post(
            "/accounts/login/?probe=1",
            data={"login": "admin", "password": "fake_bruteforce_password", "cmd": "UNION SELECT 1,2,3"},
            HTTP_USER_AGENT="Mozilla/5.0 (X11; Linux x86_64; Kali) sqlmap/1.8.2#stable",
            HTTP_X_FORWARDED_FOR="185.220.101.45, 172.68.10.12",
            HTTP_CF_IPCOUNTRY="RU",
            HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9",
            HTTP_REFERER="http://scanner-test.invalid/exploit",
            HTTP_HOST="onizukashop.com",
        )

        summary = collect_forensic_summary(
            fake_req,
            attack_type="Test Officiel Anti-Intrusion (Simulation SQLi & Scanner)",
            details="Ceci est un test déclenché via 'python manage.py test_security_alert' pour confirmer la réception des alertes d'intrusion avec toutes les informations de l'attaquant.",
            severity="critical",
            targeted_user="admin (Simulation Test IT)",
            action_taken="Simulation validée • Bouclier Onizuka opérationnel",
            ip_auto_banned=True,
        )

        ok = record_and_alert_intrusion(summary, bypass_throttle=True, sync=True)
        if ok:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[SUCCÈS] Alerte {summary['incident_id']} envoyée à {SECURITY_ALERT_EMAIL} et enregistrée en base !"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"[ÉCHEC SMTP] L'incident {summary['incident_id']} a été journalisé en BDD, mais l'email vers {SECURITY_ALERT_EMAIL} n'a pas pu partir. Vérifiez EMAIL_HOST / EMAIL_HOST_PASSWORD dans votre .env."
                )
            )
