"""
ONIZOUKA SHOP - Modeles Commandes
App: orders
Contient: Cart, CartItem, Order, OrderItem, Coupon, Address
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from shop.models import Product
import uuid
import urllib.parse


class Address(models.Model):
    """Adresse de livraison du client"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=200, verbose_name='Nom complet')
    phone = models.CharField(max_length=20, verbose_name='Telephone')
    city = models.CharField(max_length=100, verbose_name='Ville')
    district = models.CharField(max_length=100, blank=True, verbose_name='Quartier/Commune')
    address_line = models.TextField(verbose_name='Adresse complete')
    is_default = models.BooleanField(default=False, verbose_name='Adresse par defaut')

    class Meta:
        verbose_name = 'Adresse'
        verbose_name_plural = 'Adresses'

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Cart(models.Model):
    """Panier d'achat (lie a la session ou a l'utilisateur)"""
    session_key = models.CharField(max_length=40, blank=True, null=True, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    guest_email = models.EmailField(blank=True, default='', verbose_name='Email client / invité')
    guest_name = models.CharField(max_length=200, blank=True, default='', verbose_name='Nom client / invité')
    guest_phone = models.CharField(max_length=30, blank=True, default='', verbose_name='Téléphone client / invité')
    reminder_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernier rappel panier envoyé')
    reminder_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de rappels panier')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.get_full_name()}"
        return f"Panier anonyme {self.session_key}"

    def get_total(self):
        try:
            return sum((item.get_subtotal() or 0) for item in self.items.all())
        except Exception:
            return 0

    def get_items_count(self):
        try:
            return sum((item.quantity or 0) for item in self.items.all())
        except Exception:
            return 0

    def get_formatted_total(self):
        return f"{int(self.get_total()):,} FCFA".replace(",", " ")

    @property
    def whatsapp_cart_reminder_url(self):
        """Lien direct WhatsApp pour relancer un panier en attente"""
        try:
            import urllib.parse
            import re
            phone_raw = self.guest_phone or (self.user.profile.phone if (self.user and hasattr(self.user, 'profile')) else '')
            digits = re.sub(r'[^0-9]', '', str(phone_raw or ''))
            phone = ('223' + digits) if len(digits) == 8 else (digits or '22392673799')
            name = self.guest_name or (self.user.get_full_name() if self.user else '') or 'Cher client'
            total_fcfa = int(self.get_total() or 0)
            msg = (
                f"Bonjour {name}, ici ONIZUKA SHOP (Grand Marché de Bamako, Dibidani). "
                f"Vous avez laissé des appareils dans votre panier ({total_fcfa:,} FCFA). "
                f"Souhaitez-vous finaliser votre commande ?"
            ).replace(',', ' ')
            return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        except Exception:
            return "https://wa.me/22392673799"

    def get_whatsapp_cart_url(self, base_url="https://onizukashop.com"):
        """Lien direct WhatsApp pour commander les produits du panier (avec lien produit pour aperçu visuel WhatsApp)."""
        try:
            from backoffice.models import ShopSetting
            cfg = ShopSetting.get_settings()
            phone_number = cfg.whatsapp_raw
        except Exception:
            phone_number = "22392673799"
        items = list(self.items.select_related('product').all())
        if not items:
            return f"https://wa.me/{phone_number}"

        lines = [
            "Bonjour ONIZUKA SHOP,",
            "Je souhaite passer commande pour les articles suivants de mon panier :",
            "",
            "*LISTE DES ARTICLES :*",
        ]
        for item in items:
            price_formatted = f"{int(item.get_subtotal()):,} FCFA".replace(",", " ")
            addon = item.addon_details
            addon_txt = f" [+ {addon['label']}]" if addon else ""
            sku_txt = f" [{item.product.sku}]" if item.product.sku else ""
            lines.append(f"- *{item.product.name}*{sku_txt}{addon_txt} (Qté: {item.quantity}) : *{price_formatted}*")
            lines.append(f"  Voir l'appareil : {base_url}{item.product.get_absolute_url()}")

        total_formatted = f"{int(self.get_total()):,} FCFA".replace(",", " ")
        lines.extend([
            "",
            f"*TOTAL DU PANIER : {total_formatted}*",
            "Livraison : Bamako",
            "",
            "Pouvez-vous me confirmer la disponibilité et la procédure de livraison ?",
            "Merci !",
        ])

        msg = "\n".join(lines)
        return f"https://wa.me/{phone_number}?text={urllib.parse.quote(msg)}"


class CartItem(models.Model):
    """Article dans le panier"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    with_addon = models.BooleanField(default=False, verbose_name='Avec option service/accessoire')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def addon_details(self):
        if self.with_addon:
            return self.product.smart_addon
        return None

    def get_unit_total(self):
        try:
            addon = self.addon_details
            extra = addon['price'] if addon else 0
            base = getattr(self.product, 'current_price', 0) if self.product else 0
            return (base or 0) + extra
        except Exception:
            return 0

    def get_subtotal(self):
        return self.get_unit_total() * self.quantity

    def get_formatted_subtotal(self):
        return f"{int(self.get_subtotal()):,} FCFA".replace(",", " ")


class Coupon(models.Model):
    """Code promo / reduction"""

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Pourcentage (%)'
        FIXED = 'fixed', 'Montant fixe (FCFA)'

    code = models.CharField(max_length=50, unique=True, verbose_name='Code promo')
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices,
                                     default=DiscountType.PERCENTAGE, verbose_name='Type de remise')
    discount_value = models.DecimalField(max_digits=10, decimal_places=0,
                                         validators=[MinValueValidator(0)], verbose_name='Valeur')
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0,
                                           verbose_name='Commande minimum (FCFA)')
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name='Utilisations max')
    current_uses = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Date expiration')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Code promo'
        verbose_name_plural = 'Codes promo'

    def __str__(self):
        return f"{self.code} (-{self.discount_value}{'%' if self.discount_type == 'percentage' else ' FCFA'})"

    def calculate_discount(self, order_total):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return (order_total * self.discount_value) / 100
        return min(self.discount_value, order_total)


class Order(models.Model):
    """Commande client"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        CONFIRMED = 'confirmed', 'Confirmee'
        PROCESSING = 'processing', 'En preparation'
        SHIPPED = 'shipped', 'Expediee'
        DELIVERED = 'delivered', 'Livree'
        CANCELLED = 'cancelled', 'Annulee'
        REFUNDED = 'refunded', 'Remboursee'

    class PaymentMethod(models.TextChoices):
        CASH_ON_DELIVERY = 'cash_delivery', 'Paiement a la livraison'
        ORANGE_MONEY = 'orange_money', 'Orange Money'
        WAVE = 'wave', 'Wave'
        MOOV_MONEY = 'moov_money', 'Moov Money'
        BANK_TRANSFER = 'bank_transfer', 'Virement bancaire'

    @property
    def whatsapp_client_phone(self):
        """Numéro client nettoyé au format international Mali (223...) pour wa.me"""
        import re
        digits = re.sub(r'[^0-9]', '', str(self.delivery_phone or ''))
        if len(digits) == 8:
            return '223' + digits
        if digits.startswith('00'):
            return digits[2:]
        return digits

    @property
    def whatsapp_payment_reminder_url(self):
        """Lien direct WhatsApp sécurisé pour relancer le client sur sa commande en attente"""
        try:
            import urllib.parse
            phone = self.whatsapp_client_phone or '22392673799'
            total_fcfa = int(self.total or 0)
            msg = (
                f"Bonjour {self.delivery_name}, ici ONIZUKA SHOP (Grand Marché de Bamako, Dibidani). "
                f"Vos appareils pour la commande #{self.order_number} ({total_fcfa:,} FCFA) sont actuellement réservés. "
                f"Souhaitez-vous finaliser votre commande aujourd'hui ?"
            ).replace(',', ' ')
            return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        except Exception:
            return "https://wa.me/22392673799"

    order_number = models.CharField(max_length=20, unique=True, verbose_name='N° commande')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='orders', verbose_name='Client')

    # Adresse de livraison (snapshot au moment de la commande)
    delivery_name = models.CharField(max_length=200)
    delivery_phone = models.CharField(max_length=20)
    delivery_email = models.EmailField(blank=True, default='', verbose_name='Email du client')
    delivery_city = models.CharField(max_length=100)
    delivery_district = models.CharField(max_length=100, blank=True)
    delivery_address = models.TextField()

    # Suivi des emails & relances envoyés
    confirmation_email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Email confirmation envoyé le')
    payment_reminder_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernier rappel paiement envoyé le')
    payment_reminder_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de rappels envoyés')

    # Paiement
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices,
                                       default=PaymentMethod.CASH_ON_DELIVERY, verbose_name='Methode de paiement')
    payment_status = models.BooleanField(default=False, verbose_name='Paye')
    payment_reference = models.CharField(max_length=200, blank=True)

    # Totaux
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.PENDING, verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Notes client')
    admin_notes = models.TextField(blank=True, verbose_name='Notes admin')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Commande #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'ONZ' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    def get_formatted_total(self):
        return f"{int(self.total):,} FCFA".replace(",", " ")

    def get_formatted_subtotal(self):
        return f"{int(self.subtotal):,} FCFA".replace(",", " ")

    def get_formatted_shipping_cost(self):
        return f"{int(self.delivery_fee):,} FCFA".replace(",", " ")

    def get_formatted_discount(self):
        return f"{int(self.discount):,} FCFA".replace(",", " ")

    @property
    def shipping_phone(self):
        return self.delivery_phone

    @property
    def shipping_full_name(self):
        return self.delivery_name

    @property
    def shipping_city(self):
        return self.delivery_city

    @property
    def shipping_district(self):
        return self.delivery_district

    @property
    def shipping_address_line(self):
        return self.delivery_address

    @property
    def shipping_cost(self):
        return self.delivery_fee

    @property
    def discount_amount(self):
        return self.discount

    def get_status_color(self):
        colors = {
            'pending': 'yellow',
            'confirmed': 'blue',
            'processing': 'indigo',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'gray',
        }
        return colors.get(self.status, 'gray')

    def get_whatsapp_order_url(self, base_url="https://onizukashop.com"):
        """Lien direct WhatsApp pour le suivi et confirmation de la commande (avec lien produit et récapitulatif)."""
        try:
            from backoffice.models import ShopSetting
            cfg = ShopSetting.get_settings()
            phone_number = cfg.whatsapp_raw
        except Exception:
            phone_number = "22392673799"
        items = list(self.items.select_related('product').all())

        date_str = self.created_at.strftime('%d/%m/%Y à %H:%M') if self.created_at else ''
        lines = [
            "Bonjour ONIZUKA SHOP,",
            f"Voici ma commande *#{self.order_number}* enregistrée sur votre boutique :",
            "",
            f"*COMMANDE #{self.order_number}*",
            f"Date : {date_str}",
            "",
            "*ARTICLES COMMANDÉS :*",
        ]
        for item in items:
            price_formatted = f"{int(item.total_price):,} FCFA".replace(",", " ")
            sku_txt = f" [{item.product_sku}]" if item.product_sku else ""
            lines.append(f"- *{item.product_name}*{sku_txt} (x{item.quantity}) : *{price_formatted}*")
            if item.product:
                lines.append(f"  Photo & Fiche : {base_url}{item.product.get_absolute_url()}")

        total_formatted = f"{int(self.total):,} FCFA".replace(",", " ")
        lines.extend([
            "",
            f"*MONTANT TOTAL : {total_formatted}*",
            f"Mode de paiement : {self.get_payment_method_display()}",
            f"Statut actuel : {self.get_status_display()}",
            "",
            "*INFOS DE LIVRAISON :*",
            f"Client : {self.delivery_name}",
            f"Telephone : {self.delivery_phone}",
            f"Lieu : {self.delivery_district or ''}, {self.delivery_city or 'Bamako'}".strip(', '),
            f"Adresse : {self.delivery_address or 'A preciser'}",
            "",
            "Pouvez-vous me confirmer la prise en charge et le creneau de livraison ?",
            "Merci !",
        ])

        msg = "\n".join(lines)
        return f"https://wa.me/{phone_number}?text={urllib.parse.quote(msg)}"


class OrderItem(models.Model):
    """Ligne de produit dans une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)  # Snapshot du nom
    product_sku = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def get_formatted_unit_price(self):
        return f"{int(self.unit_price):,} FCFA".replace(",", " ")

    def get_formatted_total(self):
        return f"{int(self.total_price):,} FCFA".replace(",", " ")

    def get_formatted_total_price(self):
        return self.get_formatted_total()