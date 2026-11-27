"""
Commande Django : python manage.py send_email_reminders
Envoie automatiquement :
1. Les rappels de finalisation de commande / paiement Orange Money / Wave aux commandes en attente depuis > payment_reminder_hours
2. Les rappels de paniers abandonnés aux paniers non finalisés depuis > cart_abandon_reminder_hours
Respecte strictement les conditions configurées dans /gestion/emails/.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from backoffice.models import ShopSetting
from orders.models import Order, Cart
from orders.emails import send_order_payment_reminder_email, send_abandoned_cart_reminder_email


class Command(BaseCommand):
    help = "Envoie automatiquement les emails de rappel de finalisation de commande et de panier abandonné selon les délais de /gestion/emails/."

    def handle(self, *args, **options):
        cfg = ShopSetting.get_settings()
        if not cfg.email_notifications_active:
            self.stdout.write(self.style.WARNING("Notifications email globalement désactivées dans /gestion/emails/."))
            return

        now = timezone.now()
        orders_reminded = 0
        carts_reminded = 0

        # 1. Rappel de finalisation de commande non payée
        if cfg.send_payment_reminder_email:
            cutoff_order = now - timedelta(hours=max(1, cfg.payment_reminder_hours or 2))
            pending_orders = Order.objects.filter(
                status=Order.Status.PENDING,
                payment_status=False,
                created_at__lte=cutoff_order,
                payment_reminder_count=0,
            )
            for order in pending_orders:
                if send_order_payment_reminder_email(order):
                    orders_reminded += 1

        # 2. Rappel de panier abandonné
        if cfg.send_cart_abandon_reminder_email:
            cutoff_cart = now - timedelta(hours=max(1, cfg.cart_abandon_reminder_hours or 4))
            stale_carts = Cart.objects.filter(
                updated_at__lte=cutoff_cart,
                reminder_count=0,
            ).prefetch_related('items__product')
            for cart in stale_carts:
                if cart.items.exists() and send_abandoned_cart_reminder_email(cart):
                    carts_reminded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Relances terminées : {orders_reminded} commande(s) relancée(s), {carts_reminded} panier(s) relancé(s)."
            )
        )
