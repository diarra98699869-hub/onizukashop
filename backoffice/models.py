"""
ONIZOUKA SHOP - Modèles du Backoffice & Paramètres Direction
"""
from django.db import models


class ShopSetting(models.Model):
    """Configuration centrale de la boutique et paramètres opérationnels de l'entreprise."""

    # Entreprise & Siège Bamako
    site_name = models.CharField("Nom de la boutique", max_length=150, default="ONIZOUKA SHOP")
    company_name = models.CharField("Raison sociale légale", max_length=200, default="ONIZOUKA SHOP SARL")
    nif = models.CharField("Numéro d'Identification Fiscale (NIF)", max_length=100, blank=True, default="085123456M")
    rccm = models.CharField("Registre du Commerce (RCCM)", max_length=100, blank=True, default="MA-BKO-2024-B-12345")
    address = models.CharField(
        "Adresse Boutique", 
        max_length=255, 
        default="Grand Marché de Bamako, Dibidani, Bamako, Mali"
    )
    phone_contact = models.CharField("Téléphone Service Client", max_length=50, default="+223 92 67 37 99")
    phone_whatsapp = models.CharField("WhatsApp Commercial", max_length=50, default="+223 92 67 37 99")
    email_contact = models.EmailField("Email officiel", default="contact@onizoukashop.com")
    email_orders = models.EmailField("Email alertes commandes Direction", default="direction@onizoukashop.com")

    # Logistique & Livraison
    currency = models.CharField("Devise", max_length=10, default="FCFA")
    default_delivery_fee = models.DecimalField(
        "Frais de livraison forfaitaires Bamako (FCFA)", 
        max_digits=10, 
        decimal_places=0, 
        default=2000
    )
    free_delivery_threshold = models.DecimalField(
        "Seuil de livraison gratuite (FCFA)", 
        max_digits=12, 
        decimal_places=0, 
        default=500000
    )
    delivery_delay_text = models.CharField("Délai moyen affiché", max_length=100, default="Sous 24h ouvrées")
    store_pickup_active = models.BooleanField("Activer retrait gratuit magasin 15 min", default=True)

    # Moyens de Paiement
    orange_money_number = models.CharField("Numéro / Code Marchand Orange Money", max_length=50, default="+223 92 67 37 99")
    wave_number = models.CharField("Numéro Wave Mobile Money", max_length=50, default="+223 92 67 37 99")
    cash_on_delivery_active = models.BooleanField("Activer le paiement en espèces à la livraison", default=True)

    # Gestion des Stocks
    default_min_stock_alert = models.PositiveIntegerField("Seuil alerte rupture par défaut", default=5)
    block_order_on_out_of_stock = models.BooleanField("Bloquer l'achat si rupture de stock", default=True)

    # Notifications & Emails + Conditions de déclenchement
    email_notifications_active = models.BooleanField("Envoyer les emails automatiques aux clients", default=True)
    whatsapp_notifications_active = models.BooleanField("Activer les alertes rapides WhatsApp", default=True)

    # Conditions d'envoi & Alertes Email granulaires
    send_order_confirmation_email = models.BooleanField("Email client : Confirmation de commande", default=True)
    send_order_status_email = models.BooleanField("Email client : Changement de statut (Confirmée, En livraison, Livrée, Annulée)", default=True)
    send_payment_reminder_email = models.BooleanField("Email client : Rappel de finalisation de paiement (Orange Money / Wave)", default=True)
    send_cart_abandon_reminder_email = models.BooleanField("Email client : Rappel de finalisation de panier abandonné", default=True)
    send_admin_new_order_alert = models.BooleanField("Alerte Email Direction : Nouvelle commande reçue", default=True)
    send_admin_low_stock_alert = models.BooleanField("Alerte Email Direction : Stock bas ou rupture de stock", default=True)
    send_admin_contact_alert = models.BooleanField("Alerte Email Direction : Nouveau message page Contact", default=True)

    # Délais automatiques de relance
    payment_reminder_hours = models.PositiveIntegerField("Délai avant rappel de paiement non finalisé (heures)", default=2)
    cart_abandon_reminder_hours = models.PositiveIntegerField("Délai avant rappel de panier non finalisé (heures)", default=4)
    email_promo_code_reminder = models.CharField("Code promo offert dans l'email de relance panier (optionnel)", max_length=50, blank=True, default="")

    # Textes & Templates Emails Personnalisables depuis /gestion/emails/
    email_sender_name = models.CharField("Nom d'expéditeur des emails", max_length=120, default="ONIZUKA SHOP Bamako")
    email_reply_to = models.EmailField("Email de réponse (Reply-To)", blank=True, default="contact@onizukashop.com")
    email_confirmation_subject = models.CharField(
        "Objet email : Confirmation de commande",
        max_length=200,
        default="Confirmation de votre commande #{order_number} - ONIZUKA SHOP",
    )
    email_confirmation_intro = models.TextField(
        "Message d'accueil : Confirmation de commande",
        default="Votre commande a bien été enregistrée par notre équipe commerciale au Grand Marché de Bamako (Dibidani). Elle est en cours de traitement prioritaire.",
    )
    email_status_subject = models.CharField(
        "Objet email : Mise à jour statut",
        max_length=200,
        default="Commande #{order_number} : {status} - ONIZUKA SHOP",
    )
    email_status_intro = models.TextField(
        "Message d'accueil : Mise à jour statut",
        default="Le statut de votre commande chez ONIZUKA SHOP vient d'être mis à jour par notre équipe logistique à Bamako.",
    )
    email_payment_reminder_subject = models.CharField(
        "Objet email : Rappel de finalisation de commande / paiement",
        max_length=200,
        default="Finalisez votre commande #{order_number} ({total} FCFA) - ONIZUKA SHOP",
    )
    email_payment_reminder_intro = models.TextField(
        "Message : Rappel de finalisation de commande / paiement",
        default="Nous avons bien réservé vos appareils pour la commande #{order_number}. Pour déclencher l'expédition immédiate à Bamako, veuillez finaliser votre règlement Orange Money / Wave ou nous confirmer votre disponibilité.",
    )
    email_cart_reminder_subject = models.CharField(
        "Objet email : Rappel de panier en attente",
        max_length=200,
        default="Vos appareils vous attendent dans votre panier - ONIZUKA SHOP Bamako",
    )
    email_cart_reminder_intro = models.TextField(
        "Message : Rappel de panier en attente",
        default="Vous avez sélectionné des appareils dans votre panier ONIZUKA SHOP. Les stocks au Grand Marché de Bamako étant limités sur les arrivages, finalisez votre commande en 1 clic ou via WhatsApp.",
    )
    email_footer_signature = models.CharField(
        "Signature & Pied de page des emails",
        max_length=255,
        default="ONIZUKA SHOP • Grand Marché de Bamako, Dibidani • Tél & WhatsApp : +223 92 67 37 99",
    )

    # Campagnes Commerciales & Ventes Flash (Page d'accueil)
    flash_sale_active = models.BooleanField("Activer la section Ventes Flash sur l'accueil", default=True)
    flash_sale_title = models.CharField("Titre de la Vente Flash", max_length=150, default="Ventes Flash de la Semaine")
    flash_sale_subtitle = models.CharField("Sous-titre descriptif", max_length=255, default="Tarifs remisés disponibles immédiatement en stock à Bamako")
    flash_sale_end_date = models.DateTimeField("Date et heure de fin du compte à rebours", null=True, blank=True)

    # Intégration Meta Business / Facebook Ads & Tracking
    meta_pixel_id = models.CharField(
        "ID Pixel Facebook (Meta)", 
        max_length=50, 
        blank=True, 
        default="",
        help_text="Identifiant numérique Meta Pixel à 15-16 chiffres fourni par Meta Events Manager"
    )
    meta_domain_verification = models.CharField(
        "Code de vérification de domaine Meta", 
        max_length=100, 
        blank=True, 
        default="",
        help_text="Code meta name='facebook-domain-verification' fourni par Meta Business Suite"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres de la Boutique"
        verbose_name_plural = "Paramètres de la Boutique"

    def __str__(self):
        return f"Configuration {self.site_name} (Mise à jour: {self.updated_at.strftime('%d/%m/%Y')})"

    @classmethod
    def get_settings(cls):
        """Récupère l'unique configuration ou la crée avec les valeurs d'origine."""
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    @property
    def whatsapp_raw(self):
        """Format épuré pour lien wa.me (ex: 22392673799)"""
        import re
        clean = re.sub(r'[^0-9]', '', str(self.phone_whatsapp or '22392673799'))
        return clean or '22392673799'

    @property
    def whatsapp(self):
        return self.phone_whatsapp or '+223 92 67 37 99'

    @property
    def phone(self):
        return self.phone_contact or '+223 92 67 37 99'

    @property
    def flash_sale_end_iso(self):
        """Format ISO 8601 pour JavaScript (ex: 2026-09-30T23:59:59)."""
        if self.flash_sale_end_date:
            return self.flash_sale_end_date.strftime("%Y-%m-%dT%H:%M:%S")
        from django.utils import timezone
        from datetime import timedelta
        # Si date non renseignée, fin dans 3 jours à 23:59
        now = timezone.now()
        future = now + timedelta(days=3)
        return future.strftime("%Y-%m-%dT23:59:59")


class EmailLog(models.Model):
    """Journal complet de tous les emails envoyés par la plateforme (Confirmations, Statuts, Rappels, Alertes)."""

    class EmailType(models.TextChoices):
        ORDER_CONFIRMATION = 'order_confirmation', 'Confirmation de commande (Client)'
        ORDER_STATUS = 'order_status', 'Mise à jour statut commande (Client)'
        PAYMENT_REMINDER = 'payment_reminder', 'Rappel finalisation / paiement commande (Client)'
        CART_REMINDER = 'cart_reminder', 'Rappel panier abandonné (Client)'
        ADMIN_NEW_ORDER = 'admin_new_order', 'Alerte Nouvelle Commande (Direction)'
        ADMIN_LOW_STOCK = 'admin_low_stock', 'Alerte Stock Bas / Rupture (Direction)'
        ADMIN_CONTACT = 'admin_contact', 'Message Contact Visiteur (Direction)'
        TEST_EMAIL = 'test_email', 'Email de test & vérification'

    class Status(models.TextChoices):
        SENT = 'sent', 'Envoyé'
        SKIPPED = 'skipped', 'Condition désactivée'
        FAILED = 'failed', 'Échec SMTP'

    email_type = models.CharField("Type d'email", max_length=40, choices=EmailType.choices)
    recipient = models.EmailField("Destinataire")
    subject = models.CharField("Objet de l'email", max_length=255)
    status = models.CharField("Statut d'envoi", max_length=20, choices=Status.choices, default=Status.SENT)
    order_number = models.CharField("N° Commande lié", max_length=30, blank=True, default="")
    error_message = models.TextField("Détail technique / erreur", blank=True, default="")
    created_at = models.DateTimeField("Date d'envoi", auto_now_add=True)

    class Meta:
        verbose_name = "Journal d'envoi Email"
        verbose_name_plural = "Journal d'envois Emails"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_email_type_display()}] -> {self.recipient} ({self.status})"

