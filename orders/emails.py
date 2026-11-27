import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_shop_settings():
    """Récupère les paramètres de la boutique ou un fallback par défaut."""
    try:
        from backoffice.models import ShopSetting
        return ShopSetting.get_settings()
    except Exception:
        return None


def _log_email(email_type, recipient, subject, status='sent', order_number='', error_message=''):
    """Enregistre chaque tentative d'envoi d'email dans le journal EmailLog consultable sur /gestion/emails/."""
    try:
        from backoffice.models import EmailLog
        EmailLog.objects.create(
            email_type=email_type,
            recipient=recipient or 'inconnu@onizukashop.com',
            subject=subject[:255],
            status=status,
            order_number=str(order_number or '')[:30],
            error_message=str(error_message or ''),
        )
    except Exception as e:
        logger.debug(f"[EMAIL LOG] Impossible d'enregistrer le log email: {e}")


def _get_from_and_reply(shop_settings):
    """Construit l'expéditeur et le Reply-To selon les paramètres de la boutique."""
    raw_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'ONIZUKA SHOP <commandes@onizukashop.com>')
    sender_name = getattr(shop_settings, 'email_sender_name', '') or 'ONIZUKA SHOP Bamako'
    # Extraire l'adresse email pure entre <...> si présente
    if '<' in raw_from and '>' in raw_from:
        addr = raw_from.split('<', 1)[1].split('>', 1)[0].strip()
        from_email = f"{sender_name} <{addr}>"
    else:
        from_email = f"{sender_name} <{raw_from.strip()}>"

    reply_to_addr = (
        getattr(shop_settings, 'email_reply_to', '')
        or getattr(shop_settings, 'email_contact', '')
        or 'contact@onizukashop.com'
    )
    return from_email, [reply_to_addr] if reply_to_addr else None


def _resolve_order_recipient(order):
    """Récupère l'email du client (depuis delivery_email de la commande ou user.email)."""
    if getattr(order, 'delivery_email', ''):
        return order.delivery_email.strip()
    if getattr(order, 'user', None) and getattr(order.user, 'email', ''):
        return order.user.email.strip()
    return None


def _format_subject(template_str, default_str, **kwargs):
    """Formate dynamiquement un objet d'email avec les variables {order_number}, {status}, {total}."""
    raw = (template_str or default_str).strip()
    try:
        for k, v in kwargs.items():
            raw = raw.replace('{' + k + '}', str(v))
        return raw
    except Exception:
        return default_str


# ---------------------------------------------------------------------------
# 1. CONFIRMATION DE COMMANDE (CLIENT)
# ---------------------------------------------------------------------------

def send_order_confirmation_email(order, force=False):
    """
    Envoie l'email officiel de confirmation de commande au client.
    Respecte les conditions configurées dans /gestion/emails/.
    """
    shop_settings = _get_shop_settings()
    recipient_email = _resolve_order_recipient(order)

    if not recipient_email:
        logger.info(f"[EMAIL] Pas d'adresse email client pour la commande #{order.order_number}")
        return False

    total_fmt = f"{int(order.total or 0):,}".replace(',', ' ')
    subject = _format_subject(
        getattr(shop_settings, 'email_confirmation_subject', ''),
        f"Confirmation de votre commande #{order.order_number} - ONIZUKA SHOP",
        order_number=order.order_number,
        total=total_fmt,
        name=order.delivery_name,
    )

    if not force and shop_settings:
        if not shop_settings.email_notifications_active or not shop_settings.send_order_confirmation_email:
            _log_email('order_confirmation', recipient_email, subject, status='skipped', order_number=order.order_number, error_message="Désactivé dans les conditions d'envoi")
            return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    context = {
        'order': order,
        'settings': shop_settings,
        'custom_intro': getattr(shop_settings, 'email_confirmation_intro', ''),
    }

    try:
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        try:
            order.confirmation_email_sent_at = timezone.now()
            order.save(update_fields=['confirmation_email_sent_at'])
        except Exception:
            pass

        _log_email('order_confirmation', recipient_email, subject, status='sent', order_number=order.order_number)
        logger.info(f"[EMAIL] Confirmation envoyée à {recipient_email} pour #{order.order_number}")
        return True
    except Exception as e:
        _log_email('order_confirmation', recipient_email, subject, status='failed', order_number=order.order_number, error_message=str(e))
        logger.error(f"[EMAIL] Erreur confirmation #{order.order_number}: {e}")
        return False


# ---------------------------------------------------------------------------
# 2. ALERTE NOUVELLE COMMANDE (DIRECTION)
# ---------------------------------------------------------------------------

def send_admin_order_alert(order, force=False):
    """
    Alerte la direction / équipe commerciale de l'arrivée d'une nouvelle commande.
    Utilise `settings.email_orders`.
    """
    shop_settings = _get_shop_settings()
    admin_email = (
        getattr(shop_settings, 'email_orders', None)
        or getattr(shop_settings, 'email_contact', None)
        or 'direction@onizukashop.com'
    )
    total_fmt = f"{int(order.total or 0):,}".replace(',', ' ')
    subject = f"[Nouvelle Commande] #{order.order_number} - {total_fmt} FCFA ({order.delivery_name})"

    if not force and shop_settings and not shop_settings.send_admin_new_order_alert:
        _log_email('admin_new_order', admin_email, subject, status='skipped', order_number=order.order_number, error_message="Alerte direction désactivée")
        return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    context = {
        'order': order,
        'settings': shop_settings,
    }

    try:
        html_content = render_to_string('emails/admin_new_order_alert.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[admin_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        _log_email('admin_new_order', admin_email, subject, status='sent', order_number=order.order_number)
        return True
    except Exception as e:
        _log_email('admin_new_order', admin_email, subject, status='failed', order_number=order.order_number, error_message=str(e))
        logger.error(f"[EMAIL] Erreur alerte admin commande #{order.order_number}: {e}")
        return False


# ---------------------------------------------------------------------------
# 3. MISE À JOUR DU STATUT DE COMMANDE (CLIENT)
# ---------------------------------------------------------------------------

def send_order_status_update_email(order, force=False):
    """
    Notifie le client lors d'un changement de statut de sa commande.
    """
    shop_settings = _get_shop_settings()
    recipient_email = _resolve_order_recipient(order)
    if not recipient_email:
        return False

    status_label = order.get_status_display()
    total_fmt = f"{int(order.total or 0):,}".replace(',', ' ')
    subject = _format_subject(
        getattr(shop_settings, 'email_status_subject', ''),
        f"Mise à jour Commande #{order.order_number} : {status_label} - ONIZUKA SHOP",
        order_number=order.order_number,
        status=status_label,
        total=total_fmt,
        name=order.delivery_name,
    )

    if not force and shop_settings:
        if not shop_settings.email_notifications_active or not shop_settings.send_order_status_email:
            _log_email('order_status', recipient_email, subject, status='skipped', order_number=order.order_number, error_message="Notification de statut désactivée")
            return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    context = {
        'order': order,
        'settings': shop_settings,
        'custom_intro': getattr(shop_settings, 'email_status_intro', ''),
    }

    try:
        html_content = render_to_string('emails/order_status_update.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        _log_email('order_status', recipient_email, subject, status='sent', order_number=order.order_number)
        return True
    except Exception as e:
        _log_email('order_status', recipient_email, subject, status='failed', order_number=order.order_number, error_message=str(e))
        logger.error(f"[EMAIL] Erreur notification statut #{order.order_number}: {e}")
        return False


# ---------------------------------------------------------------------------
# 4. RAPPEL DE FINALISATION DE COMMANDE / PAIEMENT (ORANGE MONEY / WAVE / EN ATTENTE)
# ---------------------------------------------------------------------------

def send_order_payment_reminder_email(order, force=False):
    """
    Envoie un email de rappel de finalisation au client pour une commande non réglée / en attente,
    avec instructions Orange Money / Wave, récapitulatif des articles et bouton WhatsApp direct.
    """
    shop_settings = _get_shop_settings()
    recipient_email = _resolve_order_recipient(order)
    if not recipient_email:
        return False

    total_fmt = f"{int(order.total or 0):,}".replace(',', ' ')
    subject = _format_subject(
        getattr(shop_settings, 'email_payment_reminder_subject', ''),
        f"Finalisez votre commande #{order.order_number} ({total_fmt} FCFA) - ONIZUKA SHOP",
        order_number=order.order_number,
        total=total_fmt,
        name=order.delivery_name,
    )

    if not force and shop_settings:
        if not shop_settings.email_notifications_active or not shop_settings.send_payment_reminder_email:
            _log_email('payment_reminder', recipient_email, subject, status='skipped', order_number=order.order_number, error_message="Rappel paiement désactivé")
            return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    intro_raw = getattr(shop_settings, 'email_payment_reminder_intro', '')
    custom_intro = _format_subject(intro_raw, intro_raw, order_number=order.order_number, total=total_fmt, name=order.delivery_name)

    context = {
        'order': order,
        'settings': shop_settings,
        'custom_intro': custom_intro,
    }

    try:
        html_content = render_to_string('emails/order_payment_reminder.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        try:
            order.payment_reminder_sent_at = timezone.now()
            order.payment_reminder_count = (order.payment_reminder_count or 0) + 1
            order.save(update_fields=['payment_reminder_sent_at', 'payment_reminder_count'])
        except Exception:
            pass

        _log_email('payment_reminder', recipient_email, subject, status='sent', order_number=order.order_number)
        return True
    except Exception as e:
        _log_email('payment_reminder', recipient_email, subject, status='failed', order_number=order.order_number, error_message=str(e))
        logger.error(f"[EMAIL] Erreur rappel paiement #{order.order_number}: {e}")
        return False


# ---------------------------------------------------------------------------
# 5. RAPPEL DE FINALISATION DE PANIER ABANDONNÉ (CLIENT)
# ---------------------------------------------------------------------------

def send_abandoned_cart_reminder_email(cart, force=False):
    """
    Envoie un email de relance au client ayant laissé des articles dans son panier sans finaliser la commande.
    """
    shop_settings = _get_shop_settings()
    recipient_email = (getattr(cart, 'guest_email', '') or '').strip()
    if not recipient_email and getattr(cart, 'user', None) and getattr(cart.user, 'email', ''):
        recipient_email = cart.user.email.strip()

    if not recipient_email:
        return False

    items = list(cart.items.select_related('product').all())
    if not items:
        return False

    client_name = getattr(cart, 'guest_name', '') or (cart.user.get_full_name() if cart.user else '') or 'Cher client'
    total_fmt = f"{int(cart.get_total() or 0):,}".replace(',', ' ')
    subject = _format_subject(
        getattr(shop_settings, 'email_cart_reminder_subject', ''),
        "Vos appareils vous attendent dans votre panier - ONIZUKA SHOP Bamako",
        total=total_fmt,
        name=client_name,
    )

    if not force and shop_settings:
        if not shop_settings.email_notifications_active or not shop_settings.send_cart_abandon_reminder_email:
            _log_email('cart_reminder', recipient_email, subject, status='skipped', error_message="Rappel panier désactivé")
            return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    promo_code = (getattr(shop_settings, 'email_promo_code_reminder', '') or '').strip()

    context = {
        'cart': cart,
        'items': items,
        'client_name': client_name,
        'settings': shop_settings,
        'promo_code': promo_code,
        'custom_intro': getattr(shop_settings, 'email_cart_reminder_intro', ''),
    }

    try:
        html_content = render_to_string('emails/abandoned_cart_reminder.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        try:
            cart.reminder_sent_at = timezone.now()
            cart.reminder_count = (cart.reminder_count or 0) + 1
            cart.save(update_fields=['reminder_sent_at', 'reminder_count'])
        except Exception:
            pass

        _log_email('cart_reminder', recipient_email, subject, status='sent')
        return True
    except Exception as e:
        _log_email('cart_reminder', recipient_email, subject, status='failed', error_message=str(e))
        logger.error(f"[EMAIL] Erreur rappel panier {recipient_email}: {e}")
        return False


# ---------------------------------------------------------------------------
# 6. ALERTE MESSAGE FORMULAIRE CONTACT (DIRECTION)
# ---------------------------------------------------------------------------

def send_contact_message_email(name, phone, email, subject, message, force=False):
    """
    Alerte la direction lors de la soumission d'un message sur la page contact.
    """
    shop_settings = _get_shop_settings()
    admin_email = (
        getattr(shop_settings, 'email_orders', None)
        or getattr(shop_settings, 'email_contact', None)
        or 'direction@onizukashop.com'
    )
    email_subject = f"[Contact Boutique] Nouveau message de {name} ({phone})"

    if not force and shop_settings and not shop_settings.send_admin_contact_alert:
        _log_email('admin_contact', admin_email, email_subject, status='skipped', error_message="Alerte contact désactivée")
        return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    if email:
        reply_to = [email]

    context = {
        'name': name,
        'phone': phone,
        'email': email,
        'subject': subject,
        'message': message,
        'settings': shop_settings,
    }

    try:
        html_content = render_to_string('emails/admin_contact_message.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=text_content,
            from_email=from_email,
            to=[admin_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        _log_email('admin_contact', admin_email, email_subject, status='sent')
        return True
    except Exception as e:
        _log_email('admin_contact', admin_email, email_subject, status='failed', error_message=str(e))
        logger.error(f"[EMAIL] Erreur alerte contact: {e}")
        return False


# ---------------------------------------------------------------------------
# 7. ALERTE STOCK BAS / RUPTURE (DIRECTION)
# ---------------------------------------------------------------------------

def send_low_stock_alert_email(products, force=False):
    """
    Alerte la direction lorsqu'un ou plusieurs produits atteignent un stock bas ou une rupture.
    """
    if not products:
        return False

    shop_settings = _get_shop_settings()
    admin_email = (
        getattr(shop_settings, 'email_orders', None)
        or getattr(shop_settings, 'email_contact', None)
        or 'direction@onizukashop.com'
    )
    count = len(products)
    email_subject = f"[Alerte Stock] {count} article{'s' if count > 1 else ''} sous le seuil d'alerte à Bamako"

    if not force and shop_settings and not shop_settings.send_admin_low_stock_alert:
        _log_email('admin_low_stock', admin_email, email_subject, status='skipped', error_message="Alerte stock bas désactivée")
        return False

    from_email, reply_to = _get_from_and_reply(shop_settings)
    context = {
        'products': products,
        'settings': shop_settings,
    }

    try:
        html_content = render_to_string('emails/admin_low_stock_alert.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=text_content,
            from_email=from_email,
            to=[admin_email],
            reply_to=reply_to,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        _log_email('admin_low_stock', admin_email, email_subject, status='sent')
        return True
    except Exception as e:
        _log_email('admin_low_stock', admin_email, email_subject, status='failed', error_message=str(e))
        logger.error(f"[EMAIL] Erreur alerte stock: {e}")
        return False
