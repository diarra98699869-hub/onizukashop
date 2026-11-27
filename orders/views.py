"""
ONIZOUKA SHOP - Views Commandes
cart_add, cart_remove, cart_update, cart_detail,
checkout, order_confirm, order_history, apply_coupon
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django_htmx.http import trigger_client_event, HttpResponseClientRefresh

from shop.models import Product
from orders.models import Cart, CartItem, Order, OrderItem, Coupon, Address
from shop.views import get_or_create_cart
from orders.emails import send_order_confirmation_email, send_admin_order_alert


# ---------------------------------------------------------------------------
# Panier
# ---------------------------------------------------------------------------

def _compute_delivery_fee(subtotal, delivery_mode='delivery'):
    """Calcule dynamiquement les frais de livraison selon les paramètres /gestion/parametres/."""
    try:
        from backoffice.models import ShopSetting
        cfg = ShopSetting.get_settings()
        if delivery_mode == 'pickup' and cfg.store_pickup_active:
            return 0
        fee = int(cfg.default_delivery_fee or 0)
        threshold = int(cfg.free_delivery_threshold or 0)
        if threshold > 0 and subtotal >= threshold:
            return 0
        return max(0, fee)
    except Exception:
        return 0


def cart_detail(request):
    """Afficher le panier avec calcul de remise éventuelle par code promo et frais de livraison dynamiques"""
    try:
        cart = get_or_create_cart(request)
        items = cart.items.select_related('product', 'product__brand').prefetch_related('product__images')

        coupon = None
        coupon_id = request.session.get('coupon_id')
        if coupon_id:
            try:
                coupon = Coupon.objects.get(pk=coupon_id, is_active=True)
                if coupon.expires_at and coupon.expires_at < timezone.now():
                    coupon = None
                    del request.session['coupon_id']
                elif coupon.min_order_amount and cart.get_total() < coupon.min_order_amount:
                    pass
            except Coupon.DoesNotExist:
                coupon = None
                if 'coupon_id' in request.session:
                    del request.session['coupon_id']

        subtotal = cart.get_total()
        discount = coupon.calculate_discount(subtotal) if coupon else 0
        delivery_fee = _compute_delivery_fee(subtotal) if subtotal > 0 else 0
        total = max(0, subtotal + delivery_fee - discount)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erreur cart_detail: {e}", exc_info=True)
        cart = None
        items = []
        coupon = None
        subtotal = 0
        discount = 0
        delivery_fee = 0
        total = 0

    context = {
        'cart': cart,
        'items': items,
        'coupon': coupon,
        'subtotal': subtotal,
        'discount': discount,
        'delivery_fee': delivery_fee,
        'total': total,
        'page_title': 'Mon panier - Onizouka Shop',
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def apply_coupon(request):
    """Appliquer un code promo au panier"""
    code = request.POST.get('code', '').strip().upper()
    cart = get_or_create_cart(request)

    if not code:
        messages.error(request, 'Veuillez renseigner un code promo.')
        return redirect('orders:cart')

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        messages.error(request, f'Le code promo « {code} » est introuvable ou inactif.')
        return redirect('orders:cart')

    now = timezone.now()
    if coupon.expires_at and coupon.expires_at < now:
        messages.error(request, f'Le code promo « {code} » a expiré.')
        return redirect('orders:cart')

    if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
        messages.error(request, f'Le code promo « {code} » a atteint sa limite d\'utilisation.')
        return redirect('orders:cart')

    cart_total = cart.get_total()
    if coupon.min_order_amount and cart_total < coupon.min_order_amount:
        min_fmt = f"{int(coupon.min_order_amount):,} FCFA".replace(',', ' ')
        messages.error(request, f'Ce code nécessite un panier minimum de {min_fmt}.')
        return redirect('orders:cart')

    request.session['coupon_id'] = coupon.id
    val_str = f"-{coupon.discount_value}%" if coupon.discount_type == 'percentage' else f"-{int(coupon.discount_value):,} FCFA".replace(',', ' ')
    messages.success(request, f'Code promo « {coupon.code} » appliqué avec succès ({val_str}) !')
    return redirect('orders:cart')


def remove_coupon(request):
    """Retirer le code promo actif du panier"""
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.info(request, 'Le code promo a été retiré de votre commande.')
    return redirect('orders:cart')


@csrf_exempt
@require_POST
def cart_save_contact(request):
    """Enregistre en arrière-plan le nom, téléphone et email saisis au checkout pour les relances de panier."""
    try:
        cart = get_or_create_cart(request)
        email = (request.POST.get('email') or '').strip()
        name = (request.POST.get('name') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        fields = []
        if email:
            cart.guest_email = email[:254]
            fields.append('guest_email')
        if name:
            cart.guest_name = name[:200]
            fields.append('guest_name')
        if phone:
            cart.guest_phone = phone[:30]
            fields.append('guest_phone')
        if fields:
            cart.save(update_fields=fields)
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'ignored'})



@csrf_exempt
def cart_add(request, product_id):
    """Ajouter un produit au panier (POST ou GET résilient, exempt CSRF)"""
    try:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        cart = get_or_create_cart(request)

        qty_raw = request.POST.get('quantity') or request.GET.get('quantity', 1)
        try:
            quantity = int(qty_raw)
        except (ValueError, TypeError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        is_ajax = (
            getattr(request, 'htmx', False) or 
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
            'application/json' in request.headers.get('accept', '') or
            request.POST.get('format') == 'json'
        )

        # Verifier le stock
        if product.track_stock and product.stock < quantity:
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'Stock insuffisant ({product.stock} dispo)'}, status=400)
            messages.error(request, f'Stock insuffisant. Seulement {product.stock} disponibles.')
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer else 'shop:product', slug=product.slug)

        with_addon = str(request.POST.get('with_addon') or request.GET.get('with_addon') or '').lower() in ('1', 'true', 'on')

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            new_qty = cart_item.quantity + quantity
            if product.track_stock and product.stock < new_qty:
                new_qty = product.stock
            cart_item.quantity = new_qty
            if with_addon:
                cart_item.with_addon = True
            cart_item.save(update_fields=['quantity', 'with_addon'])
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity, with_addon=with_addon)

        cart_count = cart.get_items_count()

        if is_ajax:
            response = JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'product_name': product.name,
                'message': f'"{product.name}" ajouté au panier !',
            })
            trigger_client_event(response, 'cartUpdated', {
                'count': cart_count,
                'message': f'"{product.name}" ajouté au panier !',
            })
            return response

        messages.success(request, f'"{product.name}" ajouté au panier !')
        next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER')
        if next_url and '/panier/ajouter/' not in next_url:
            return redirect(next_url)
        return redirect('orders:cart')
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Erreur cart_add: {e}", exc_info=True)
        is_ajax = (
            getattr(request, 'htmx', False) or 
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
            'application/json' in request.headers.get('accept', '')
        )
        if is_ajax:
            return JsonResponse({'success': False, 'message': "Erreur lors de l'ajout au panier"}, status=400)
        messages.error(request, "Impossible d'ajouter cet article au panier.")
        referer = request.META.get('HTTP_REFERER')
        if referer and '/panier/ajouter/' not in referer:
            return redirect(referer)
        return redirect('orders:cart')


@require_POST
def cart_remove(request, item_id):
    """Supprimer un article du panier"""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    product_name = item.product.name
    item.delete()

    if request.htmx:
        cart.refresh_from_db()
        context = {
            'cart': cart,
            'items': cart.items.select_related('product').prefetch_related('product__images'),
        }
        response = render(request, 'orders/partials/cart_items.html', context)
        trigger_client_event(response, 'cartUpdated', {'count': cart.get_items_count()})
        return response

    messages.success(request, f'"{product_name}" retire du panier.')
    return redirect('orders:cart')


@require_POST
def cart_update(request, item_id):
    """Mettre a jour la quantite d'un article"""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
    else:
        if item.product.track_stock and item.product.stock < quantity:
            quantity = item.product.stock
        item.quantity = quantity
        item.save()

    if request.htmx:
        cart.refresh_from_db()
        context = {
            'cart': cart,
            'items': cart.items.select_related('product').prefetch_related('product__images'),
        }
        response = render(request, 'orders/partials/cart_items.html', context)
        trigger_client_event(response, 'cartUpdated', {'count': cart.get_items_count()})
        return response

    return redirect('orders:cart')


# ---------------------------------------------------------------------------
# Accès sécurisé aux commandes (Client connecté + Commande express invité)
# ---------------------------------------------------------------------------

def _get_accessible_order(request, order_number):
    """Autorise le client propriétaire, le staff, ou l'acheteur invité de la session courante."""
    from django.http import Http404
    qs = Order.objects.select_related('user').prefetch_related('items__product__images')
    order = get_object_or_404(qs, order_number=order_number)
    if request.user.is_authenticated and (request.user.is_staff or order.user_id == request.user.id):
        return order
    guest_orders = request.session.get('guest_orders') or []
    if order.order_number in guest_orders:
        return order
    raise Http404("Commande introuvable.")


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

def checkout(request):
    """Page de commande / livraison / paiement (Client connecté ou Invité rapide)"""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, 'Votre panier est vide.')
        return redirect('orders:cart')

    items = cart.items.select_related('product').prefetch_related('product__images')
    if request.user.is_authenticated:
        addresses = Address.objects.filter(user=request.user)
        default_address = addresses.filter(is_default=True).first() or addresses.first()
        user_phone = getattr(getattr(request.user, 'profile', None), 'phone', '') or ''
        user_full_name = request.user.get_full_name() or request.user.username
    else:
        addresses = []
        default_address = None
        user_phone = ''
        user_full_name = ''

    # Code promo en session
    coupon = None
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(pk=coupon_id, is_active=True)
        except Coupon.DoesNotExist:
            del request.session['coupon_id']

    subtotal = cart.get_total()
    delivery_fee = _compute_delivery_fee(subtotal)
    discount = coupon.calculate_discount(subtotal) if coupon else 0
    total = max(0, subtotal + delivery_fee - discount)

    context = {
        'cart': cart,
        'items': items,
        'addresses': addresses,
        'default_address': default_address,
        'user_phone': user_phone,
        'user_full_name': user_full_name,
        'coupon': coupon,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'shipping': delivery_fee,
        'discount': discount,
        'total': total,
        'payment_methods': Order.PaymentMethod.choices,
        'page_title': 'Finaliser la commande - Onizouka Shop',
    }
    return render(request, 'orders/checkout.html', context)


@require_POST
def place_order(request):
    """Valider et creer la commande (Connecté ou Invité)"""
    import threading
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, 'Votre panier est vide.')
        return redirect('orders:cart')

    # Recuperer les donnees du formulaire
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    delivery_email = request.POST.get('delivery_email', '').strip()
    if not delivery_email and request.user.is_authenticated and request.user.email:
        delivery_email = request.user.email.strip()
    city = request.POST.get('city', '').strip() or 'Bamako'
    district = request.POST.get('district', '').strip()
    address_line = request.POST.get('address_line', '').strip()
    raw_payment = request.POST.get('payment_method', Order.PaymentMethod.CASH_ON_DELIVERY).strip()
    if raw_payment == 'cash_on_delivery':
        raw_payment = Order.PaymentMethod.CASH_ON_DELIVERY
    valid_methods = {code for code, _ in Order.PaymentMethod.choices}
    payment_method = raw_payment if raw_payment in valid_methods else Order.PaymentMethod.CASH_ON_DELIVERY

    notes = request.POST.get('notes', '').strip()
    payment_reference = request.POST.get('payment_reference', '').strip()
    save_address = request.POST.get('save_address') == 'on'

    if not all([full_name, phone, address_line]):
        messages.error(request, 'Veuillez renseigner votre nom, téléphone et adresse de livraison.')
        return redirect('orders:checkout')

    # Code promo
    coupon = None
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(pk=coupon_id, is_active=True)
        except Coupon.DoesNotExist:
            pass

    items = list(cart.items.select_related('product').all())
    subtotal = cart.get_total()
    delivery_mode = (request.POST.get('delivery_mode') or 'delivery').strip()
    delivery_fee = _compute_delivery_fee(subtotal, delivery_mode=delivery_mode)
    discount = coupon.calculate_discount(subtotal) if coupon else 0
    total = max(0, subtotal + delivery_fee - discount)

    # Creer la commande
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        delivery_name=full_name,
        delivery_phone=phone,
        delivery_email=delivery_email,
        delivery_city=city,
        delivery_district=district,
        delivery_address=address_line,
        payment_method=payment_method,
        payment_reference=payment_reference,
        coupon=coupon,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        discount=discount,
        total=total,
        notes=notes,
    )

    # Mémoriser dans la session pour accès immédiat (invité ou connecté)
    guest_orders = list(request.session.get('guest_orders') or [])
    if order.order_number not in guest_orders:
        guest_orders.append(order.order_number)
        request.session['guest_orders'] = guest_orders[-20:]

    # Creer les lignes de commande et surveiller les stocks bas
    low_stock_products = []
    for item in items:
        addon = item.addon_details
        snap_name = f"{item.product.name} (+ {addon['label']})" if addon else item.product.name
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=snap_name[:300],
            product_sku=item.product.sku,
            quantity=item.quantity,
            unit_price=item.get_unit_total(),
        )
        # Decrementer le stock
        if item.product.track_stock:
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save(update_fields=['stock', 'status'])
            if item.product.stock <= item.product.min_stock:
                low_stock_products.append(item.product)

    # Incrementer utilisation coupon
    if coupon:
        coupon.current_uses += 1
        coupon.save(update_fields=['current_uses'])
        if 'coupon_id' in request.session:
            del request.session['coupon_id']

    # Sauvegarder l'adresse si demande et connecté
    if save_address and request.user.is_authenticated:
        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            city=city,
            district=district,
            address_line=address_line,
            is_default=not Address.objects.filter(user=request.user).exists()
        )

    # Vider le panier
    cart.items.all().delete()

    # Envoi asynchrone non-bloquant des emails transactionnels
    def _send_emails_bg(ord_obj, low_stock_list):
        try:
            send_order_confirmation_email(ord_obj)
            send_admin_order_alert(ord_obj)
            if low_stock_list:
                from orders.emails import send_low_stock_alert_email
                send_low_stock_alert_email(low_stock_list)
        except Exception:
            pass

    threading.Thread(target=_send_emails_bg, args=(order, low_stock_products), daemon=True).start()

    messages.success(request, f'Commande #{order.order_number} enregistrée ! Merci pour votre achat.')
    return redirect('orders:confirmation', order_number=order.order_number)


# ---------------------------------------------------------------------------
# Confirmation
# ---------------------------------------------------------------------------

def order_confirmation(request, order_number):
    """Page de confirmation de commande avec possibilité d'ajouter la référence de paiement"""
    order = _get_accessible_order(request, order_number)

    if request.method == 'POST':
        ref = request.POST.get('payment_reference', '').strip()
        if ref:
            order.payment_reference = ref
            order.save(update_fields=['payment_reference'])
            messages.success(request, f"Référence de transaction {ref} enregistrée. Notre équipe vérifie votre dépôt.")
            return redirect('orders:confirmation', order_number=order.order_number)

    items = order.items.select_related('product').prefetch_related('product__images')

    context = {
        'order': order,
        'items': items,
        'page_title': f'Commande #{order.order_number} confirmée - Onizouka Shop',
    }
    return render(request, 'orders/confirmation.html', context)


# ---------------------------------------------------------------------------
# Historique des commandes
# ---------------------------------------------------------------------------

@login_required
def order_history(request):
    """Liste des commandes de l'utilisateur"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product__images').order_by('-created_at')

    context = {
        'orders': orders,
        'page_title': 'Mes commandes - Onizouka Shop',
    }
    return render(request, 'orders/history.html', context)


def order_detail(request, order_number):
    """Detail d'une commande"""
    order = _get_accessible_order(request, order_number)
    items = order.items.select_related('product').prefetch_related('product__images')

    context = {
        'order': order,
        'items': items,
        'page_title': f'Commande #{order.order_number} - Onizouka Shop',
    }
    return render(request, 'orders/order_detail.html', context)


def order_invoice(request, order_number):
    """Facture et bordereau officiel téléchargeable/imprimable pour le client."""
    qs = Order.objects.select_related('user').prefetch_related('items__product')
    try:
        order = _get_accessible_order(request, order_number)
    except Exception:
        order = get_object_or_404(qs, order_number=order_number)

    try:
        from backoffice.models import ShopSetting
        settings_obj = ShopSetting.get_settings()
    except Exception:
        settings_obj = None

    return render(request, 'backoffice/order_invoice.html', {
        'order': order,
        'settings': settings_obj,
        'is_client_view': True,
    })


def track_order_public(request):
    """Suivi public de commande sans connexion obligatoire (N° ONZ... + Téléphone)."""
    import re
    found_order = None
    order_num_input = (request.GET.get('order_number') or request.POST.get('order_number') or '').strip().upper().lstrip('#')
    phone_input = (request.GET.get('phone') or request.POST.get('phone') or '').strip()

    if order_num_input and not order_num_input.startswith('ONZ') and order_num_input.isdigit():
        order_num_input = 'ONZ' + order_num_input

    searched = bool(order_num_input or phone_input)
    error_msg = ''

    if searched:
        digits_in = re.sub(r'[^0-9]', '', phone_input)
        if not order_num_input or len(digits_in) < 6:
            error_msg = "Veuillez saisir votre numéro de commande (ex: ONZ...) et votre numéro de téléphone."
        else:
            candidate = (
                Order.objects
                .select_related('user')
                .prefetch_related('items__product__images')
                .filter(order_number__iexact=order_num_input)
                .first()
            )
            if candidate:
                cand_digits = re.sub(r'[^0-9]', '', candidate.delivery_phone or '')
                if cand_digits[-8:] == digits_in[-8:] or (request.user.is_authenticated and (request.user.is_staff or candidate.user_id == request.user.id)):
                    found_order = candidate
                    guest_orders = list(request.session.get('guest_orders') or [])
                    if found_order.order_number not in guest_orders:
                        guest_orders.append(found_order.order_number)
                        request.session['guest_orders'] = guest_orders[-20:]
                else:
                    error_msg = "Le numéro de téléphone ne correspond pas à cette commande."
            else:
                error_msg = f"Aucune commande trouvée avec la référence « {order_num_input} »."

    return render(request, 'orders/track.html', {
        'order': found_order,
        'order_number_val': order_num_input,
        'phone_val': phone_input,
        'searched': searched,
        'error_msg': error_msg,
        'page_title': 'Suivre ma commande - Onizouka Shop',
    })

