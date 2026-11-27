"""
ONIZOUKA SHOP - Vues du Backoffice Direction & Gestion
Corrections audit : N+1 SQL, erreurs silencieuses, HTML hardcodé, endpoints sécurisés
"""
import csv
import io
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.conf import settings

from orders.models import Order, OrderItem, Address
from shop.models import Product, Category, Brand, ProductImage
from inventory.models import StockMovement, Supplier
from accounts.models import UserProfile
from orders.emails import send_order_status_update_email
from .forms import ProductForm, StockSupplyForm, OrderUpdateForm


# ---------------------------------------------------------------------------
# Décorateur de sécurité
# ---------------------------------------------------------------------------

def staff_required(view_func):
    """Décorateur : seul le personnel Onizouka Shop (is_staff) peut accéder."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter avec vos identifiants Direction.")
            login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
            return redirect(f"{login_url}?next={request.path}")
        if not request.user.is_staff:
            messages.error(request, "Accès refusé : espace réservé exclusivement à la Direction Onizouka Shop.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ---------------------------------------------------------------------------
# Tableau de bord exécutif
# ---------------------------------------------------------------------------

@staff_required
def dashboard_view(request):
    """Tableau de bord exécutif de la Direction Onizouka Shop avec filtre de caisse journalier."""
    from datetime import timedelta
    now = timezone.localtime(timezone.now())
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_7d = start_of_today - timedelta(days=6)
    first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    valid_statuses_exclude = [Order.Status.CANCELLED, Order.Status.REFUNDED]

    period = (request.GET.get('period') or 'today').strip()
    valid_orders = Order.objects.exclude(status__in=valid_statuses_exclude)

    if period == 'today':
        scoped_orders = valid_orders.filter(created_at__gte=start_of_today)
        period_label = "Aujourd'hui"
    elif period == '7d':
        scoped_orders = valid_orders.filter(created_at__gte=start_7d)
        period_label = "7 derniers jours"
    elif period == 'month':
        scoped_orders = valid_orders.filter(created_at__gte=first_day_month)
        period_label = "Mois en cours"
    else:
        period = 'all'
        scoped_orders = valid_orders
        period_label = "Cumul global"

    total_revenue = valid_orders.aggregate(total=Sum('total'))['total'] or 0
    month_revenue = valid_orders.filter(created_at__gte=first_day_month).aggregate(total=Sum('total'))['total'] or 0
    today_revenue = valid_orders.filter(created_at__gte=start_of_today).aggregate(total=Sum('total'))['total'] or 0
    today_orders_count = valid_orders.filter(created_at__gte=start_of_today).count()

    period_revenue = scoped_orders.aggregate(total=Sum('total'))['total'] or 0
    period_paid_revenue = scoped_orders.filter(payment_status=True).aggregate(total=Sum('total'))['total'] or 0
    period_orders_count = scoped_orders.count()

    total_orders_count = Order.objects.count()
    pending_orders_count = Order.objects.filter(
        status__in=[Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.PROCESSING]
    ).count()

    low_stock_qs = Product.objects.filter(
        track_stock=True,
        stock__lte=F('min_stock'),
        is_active=True
    ).select_related('category', 'brand').order_by('stock')
    low_stock_count = low_stock_qs.count()
    low_stock_products = low_stock_qs[:6]

    total_customers_count = User.objects.filter(is_staff=False, is_superuser=False).count()

    recent_orders = (
        Order.objects
        .select_related('user')
        .prefetch_related('items')
        .order_by('-created_at')[:8]
    )

    count_by_payment = {
        r['payment_method']: r['count']
        for r in scoped_orders.values('payment_method').annotate(count=Count('id'))
    }
    volume_by_payment = {
        r['payment_method']: r['volume'] or 0
        for r in scoped_orders.values('payment_method').annotate(volume=Sum('total'))
    }
    payment_methods_stats = [
        {
            'code': code,
            'label': label,
            'count': count_by_payment.get(code, 0),
            'volume': volume_by_payment.get(code, 0),
        }
        for code, label in Order.PaymentMethod.choices
    ]

    total_stock_units = (
        Product.objects.filter(track_stock=True).aggregate(units=Sum('stock'))['units'] or 0
    )

    context = {
        'period': period,
        'period_label': period_label,
        'period_revenue': period_revenue,
        'period_paid_revenue': period_paid_revenue,
        'period_orders_count': period_orders_count,
        'today_revenue': today_revenue,
        'today_orders_count': today_orders_count,
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'total_customers_count': total_customers_count,
        'total_stock_units': total_stock_units,
        'recent_orders': recent_orders,
        'payment_methods_stats': payment_methods_stats,
        'current_page': 'dashboard',
    }
    return render(request, 'backoffice/dashboard.html', context)


# ---------------------------------------------------------------------------
# Commandes
# ---------------------------------------------------------------------------

@staff_required
def orders_view(request):
    """Gestion complète des commandes clients avec filtres et recherche."""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()
    payment_filter = request.GET.get('payment', '')

    orders_qs = (
        Order.objects
        .select_related('user')
        .prefetch_related('items__product')
        .order_by('-created_at')
    )

    if status_filter and status_filter != 'all':
        orders_qs = orders_qs.filter(status=status_filter)
    if payment_filter:
        orders_qs = orders_qs.filter(payment_method=payment_filter)
    if search_query:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=search_query) |
            Q(delivery_name__icontains=search_query) |
            Q(delivery_phone__icontains=search_query) |
            Q(delivery_district__icontains=search_query) |
            Q(delivery_city__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Comptage des statuts : UNE seule requête annotée au lieu de 7 COUNT séparés
    count_by_status = {
        r['status']: r['count']
        for r in Order.objects.values('status').annotate(count=Count('id'))
    }
    status_counts = {
        'all': sum(count_by_status.values()),
        'pending': count_by_status.get(Order.Status.PENDING, 0),
        'confirmed': count_by_status.get(Order.Status.CONFIRMED, 0),
        'processing': count_by_status.get(Order.Status.PROCESSING, 0),
        'shipped': count_by_status.get(Order.Status.SHIPPED, 0),
        'delivered': count_by_status.get(Order.Status.DELIVERED, 0),
        'cancelled': count_by_status.get(Order.Status.CANCELLED, 0),
    }

    paginator = Paginator(orders_qs, 20)
    page_number = request.GET.get('page', 1)
    orders = paginator.get_page(page_number)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'search_query': search_query,
        'payment_filter': payment_filter,
        'payment_choices': Order.PaymentMethod.choices,
        'status_choices': Order.Status.choices,
        'current_page': 'orders',
    }
    return render(request, 'backoffice/orders_list.html', context)


@staff_required
def order_detail_view(request, order_id):
    """Détail complet et modification du statut d'une commande."""
    order = get_object_or_404(
        Order.objects.select_related('user', 'coupon').prefetch_related('items__product__images'),
        id=order_id,
    )

    if request.method == 'POST':
        quick_action = request.POST.get('quick_action', '').strip()
        if quick_action:
            prev_status = order.status
            if quick_action == 'confirm':
                order.status = Order.Status.CONFIRMED
            elif quick_action == 'ship':
                order.status = Order.Status.SHIPPED
            elif quick_action == 'deliver':
                order.status = Order.Status.DELIVERED
                order.payment_status = True
                if not order.delivered_at:
                    order.delivered_at = timezone.now()
            elif quick_action == 'mark_paid':
                order.payment_status = True
            elif quick_action == 'send_payment_reminder':
                from orders.emails import send_order_payment_reminder_email
                sent = send_order_payment_reminder_email(order, force=True)
                if sent:
                    messages.success(request, f"Email de rappel de finalisation envoyé pour la commande #{order.order_number}.")
                else:
                    messages.warning(request, f"Impossible d'envoyer l'email : renseignez d'abord l'email du client dans « Modifier adresse / remise / frais ».")
                return redirect('backoffice:order_detail', order_id=order.id)
            elif quick_action == 'resend_confirmation':
                from orders.emails import send_order_confirmation_email
                sent = send_order_confirmation_email(order, force=True)
                if sent:
                    messages.success(request, f"Email de confirmation renvoyé au client pour la commande #{order.order_number}.")
                else:
                    messages.warning(request, f"Impossible d'envoyer l'email : renseignez d'abord l'email du client dans la fiche commande.")
                return redirect('backoffice:order_detail', order_id=order.id)
            elif quick_action == 'cancel':
                if order.status != Order.Status.CANCELLED:
                    for item in order.items.select_related('product').all():
                        if item.product and item.product.track_stock:
                            before = item.product.stock
                            item.product.stock += item.quantity
                            if item.product.stock > 0 and item.product.status == Product.Status.OUT_OF_STOCK:
                                item.product.status = Product.Status.ACTIVE
                            item.product.save(update_fields=['stock', 'status'])
                            StockMovement.objects.create(
                                product=item.product,
                                movement_type=StockMovement.MovementType.RETURN,
                                quantity=item.quantity,
                                stock_before=before,
                                stock_after=item.product.stock,
                                reference=f"Annulation #{order.order_number}",
                                notes="Retour automatique en stock suite à annulation commande",
                                created_by=request.user,
                            )
                order.status = Order.Status.CANCELLED
            order.save()
            if prev_status != order.status:
                send_order_status_update_email(order)
            messages.success(request, f"Commande #{order.order_number} mise à jour.")
            return redirect('backoffice:order_detail', order_id=order.id)

        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            prev_status = order.status
            updated_order = form.save(commit=False)
            # Recalculer le total net si remise ou frais de livraison ont été ajustés
            fee = int(updated_order.delivery_fee or 0)
            disc = int(updated_order.discount or 0)
            sub = int(updated_order.subtotal or 0)
            updated_order.total = max(0, sub + fee - disc)

            # Si passage en annulé via le menu déroulant, recréditer le stock
            if updated_order.status == Order.Status.CANCELLED and prev_status != Order.Status.CANCELLED:
                for item in order.items.select_related('product').all():
                    if item.product and item.product.track_stock:
                        before = item.product.stock
                        item.product.stock += item.quantity
                        if item.product.stock > 0 and item.product.status == Product.Status.OUT_OF_STOCK:
                            item.product.status = Product.Status.ACTIVE
                        item.product.save(update_fields=['stock', 'status'])
                        StockMovement.objects.create(
                            product=item.product,
                            movement_type=StockMovement.MovementType.RETURN,
                            quantity=item.quantity,
                            stock_before=before,
                            stock_after=item.product.stock,
                            reference=f"Annulation #{order.order_number}",
                            notes="Retour stock auto",
                            created_by=request.user,
                        )

            # Horodatage livraison sans double save()
            if updated_order.status == Order.Status.DELIVERED and prev_status != Order.Status.DELIVERED:
                updated_order.delivered_at = timezone.now()
            updated_order.save()

            # Notification par email si le statut a changé
            if prev_status != updated_order.status:
                send_order_status_update_email(updated_order)

            messages.success(request, f"La commande #{order.order_number} a été mise à jour avec succès.")
            return redirect('backoffice:order_detail', order_id=order.id)
    else:
        form = OrderUpdateForm(instance=order)

    import re
    raw_phone = re.sub(r'[^0-9]', '', str(order.delivery_phone or ''))
    if raw_phone and len(raw_phone) == 8:
        raw_phone = '223' + raw_phone

    client_previous_orders = []
    if order.user:
        client_previous_orders = (
            Order.objects
            .filter(user=order.user)
            .exclude(id=order.id)
            .order_by('-created_at')[:5]
        )

    context = {
        'order': order,
        'client_wa_phone': raw_phone,
        'form': form,
        'client_previous_orders': client_previous_orders,
        'status_choices': Order.Status.choices,
        'current_page': 'orders',
    }
    return render(request, 'backoffice/order_detail.html', context)


@staff_required
def order_invoice_view(request, order_id):
    """Bordereau de livraison / Facture officiel Onizouka Shop imprimable."""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id,
    )
    return render(request, 'backoffice/order_invoice.html', {'order': order})


@staff_required
@require_POST
def order_quick_list_action_view(request, order_id):
    """Action express 1-clic depuis la liste mobile/PC des commandes (Confirmer, Encaisser, Livrer)."""
    order = get_object_or_404(Order, id=order_id)
    action = (request.POST.get('quick_action') or '').strip()
    prev_status = order.status

    if action == 'confirm':
        order.status = Order.Status.CONFIRMED
    elif action == 'mark_paid':
        order.payment_status = True
    elif action == 'ship':
        order.status = Order.Status.SHIPPED
    elif action == 'deliver':
        order.status = Order.Status.DELIVERED
        order.payment_status = True
        if not order.delivered_at:
            order.delivered_at = timezone.now()

    order.save()
    if prev_status != order.status:
        try:
            send_order_status_update_email(order)
        except Exception:
            pass

    messages.success(request, f"Commande #{order.order_number} mise à jour.")
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/gestion/'):
        return redirect(next_url)
    return redirect('backoffice:orders')


@staff_required
def pos_order_create_view(request):
    """Caisse Express 15s : Enregistrer une vente conclue sur WhatsApp ou au comptoir Dibidani."""
    import json
    products_qs = (
        Product.objects.filter(is_active=True)
        .select_related('category', 'brand')
        .prefetch_related('images')
        .order_by('name')
    )

    if request.method == 'POST':
        client_name = (request.POST.get('delivery_name') or 'Client Boutique').strip()
        client_phone = (request.POST.get('delivery_phone') or '+223 00 00 00 00').strip()
        client_district = (request.POST.get('delivery_district') or 'Grand Marché Dibidani').strip()
        client_address = (request.POST.get('delivery_address') or 'Vente directe boutique / WhatsApp').strip()
        payment_method = (request.POST.get('payment_method') or Order.PaymentMethod.CASH_ON_DELIVERY).strip()
        paid_now = request.POST.get('paid_now') == 'on'
        delivered_now = request.POST.get('delivered_now') == 'on'
        notes = (request.POST.get('notes') or '').strip()

        raw_lines = request.POST.get('lines_json') or '[]'
        try:
            lines = json.loads(raw_lines)
        except Exception:
            lines = []

        valid_lines = []
        for ln in lines:
            try:
                pid = int(ln.get('product_id'))
                qty = max(1, int(ln.get('quantity', 1)))
                prod = Product.objects.filter(id=pid).first()
                if not prod:
                    continue
                uprice = max(0, int(float(ln.get('unit_price', prod.current_price))))
                valid_lines.append((prod, qty, uprice))
            except Exception:
                continue

        if not valid_lines:
            messages.error(request, "Veuillez sélectionner au moins un article pour enregistrer la vente.")
        else:
            subtotal = sum(qty * uprice for _, qty, uprice in valid_lines)
            status_val = Order.Status.DELIVERED if delivered_now else Order.Status.CONFIRMED
            order = Order.objects.create(
                delivery_name=client_name,
                delivery_phone=client_phone,
                delivery_city='Bamako',
                delivery_district=client_district,
                delivery_address=client_address,
                payment_method=payment_method,
                payment_status=paid_now or delivered_now,
                subtotal=subtotal,
                delivery_fee=0,
                discount=0,
                total=subtotal,
                status=status_val,
                delivered_at=timezone.now() if delivered_now else None,
                admin_notes=f"Saisie Caisse / WhatsApp par {request.user.username}. {notes}".strip(),
            )
            for prod, qty, uprice in valid_lines:
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_name=prod.name,
                    product_sku=prod.sku,
                    quantity=qty,
                    unit_price=uprice,
                )
                if prod.track_stock:
                    before = prod.stock
                    prod.stock = max(0, prod.stock - qty)
                    if prod.stock == 0:
                        prod.status = Product.Status.OUT_OF_STOCK
                    prod.save(update_fields=['stock', 'status'])
                    StockMovement.objects.create(
                        product=prod,
                        movement_type=StockMovement.MovementType.OUT,
                        quantity=qty,
                        stock_before=before,
                        stock_after=prod.stock,
                        reference=f"Vente #{order.order_number}",
                        notes=f"Client: {client_name}",
                        created_by=request.user,
                    )

            messages.success(request, f"Vente #{order.order_number} enregistrée ({int(subtotal):,} FCFA) ! Facture et reçu WhatsApp prêts.".replace(',', ' '))
            return redirect('backoffice:order_detail', order_id=order.id)

    catalog_data = []
    for p in products_qs:
        thumb = ''
        if p.primary_image:
            try:
                thumb = p.primary_image.thumbnail.url
            except Exception:
                thumb = p.primary_image.image.url
        catalog_data.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'category': p.category.short_name,
            'price': int(p.current_price),
            'stock': p.stock,
            'thumb': thumb,
        })

    return render(request, 'backoffice/pos_order_create.html', {
        'catalog_json': json.dumps(catalog_data),
        'payment_choices': Order.PaymentMethod.choices,
        'current_page': 'orders',
    })


@staff_required
@require_POST  # Sécurité : endpoint HTMX accessible en POST uniquement
def update_order_status_htmx(request, order_id):
    """Changement de statut rapide en 1 clic via HTMX."""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    if new_status in dict(Order.Status.choices):
        prev_status = order.status
        order.status = new_status
        if new_status == Order.Status.DELIVERED and not order.delivered_at:
            order.delivered_at = timezone.now()
        order.save(update_fields=['status', 'delivered_at'])
        
        # Envoi de la notification client par email
        if prev_status != new_status:
            send_order_status_update_email(order)

    return render(request, 'backoffice/partials/order_status_badge.html', {'order': order})


# ---------------------------------------------------------------------------
# Catalogue & Produits
# ---------------------------------------------------------------------------

@staff_required
def products_view(request):
    """Catalogue complet des produits avec prix, stocks et statut."""
    category_slug = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    stock_status = request.GET.get('stock', '')
    search_query = request.GET.get('q', '').strip()

    products_qs = (
        Product.objects
        .select_related('category', 'brand')
        .prefetch_related('images')
        .order_by('-created_at')
    )

    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)
    if brand_id:
        products_qs = products_qs.filter(brand_id=brand_id)
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    if stock_status == 'low':
        products_qs = products_qs.filter(track_stock=True, stock__lte=F('min_stock'), stock__gt=0)
    elif stock_status == 'out':
        products_qs = products_qs.filter(track_stock=True, stock=0)
    
    featured_filter = request.GET.get('featured', '')
    if featured_filter == '1':
        products_qs = products_qs.filter(is_featured=True)

    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    total_filtered_count = products_qs.count()
    total_products_count = Product.objects.count()

    paginator = Paginator(products_qs, 25)
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category': category_slug,
        'selected_brand': brand_id,
        'selected_stock': stock_status,
        'selected_featured': featured_filter,
        'search_query': search_query,
        'total_filtered_count': total_filtered_count,
        'total_products_count': total_products_count,
        'current_page': 'products',
    }
    return render(request, 'backoffice/products_list.html', context)


@staff_required
def product_create_view(request):
    """Ajout rapide ou complet d'un nouveau produit par la Direction (avec découpe 15s & compression 8 Mo auto)."""
    from django.core.exceptions import ValidationError
    from shop.video_utils import process_uploaded_product_video

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = form.cleaned_data['category']
            product.brand = form.cleaned_data.get('brand')
            product.description = form.cleaned_data['description']
            if not product.addon_price:
                product.addon_price = 0

            raw_specs = (request.POST.get('specifications_json') or '').strip()
            if raw_specs:
                import json
                try:
                    parsed_specs = json.loads(raw_specs)
                    if isinstance(parsed_specs, dict):
                        product.specifications = parsed_specs
                except Exception:
                    pass

            video_ok = True
            if 'video_file' in request.FILES:
                try:
                    processed_video, v_info = process_uploaded_product_video(request.FILES['video_file'])
                    product.video_file = processed_video
                    if v_info.get('summary'):
                        messages.info(request, v_info['summary'])
                except ValidationError as ve:
                    video_ok = False
                    err_txt = ve.messages[0] if hasattr(ve, 'messages') and ve.messages else str(ve)
                    form.add_error(None, err_txt)
                    messages.error(request, err_txt)

            if video_ok:
                product.save()
                try:
                    from django.core.cache import cache
                    cache.delete('menu_categories_cached')
                except Exception:
                    pass
                if 'primary_image' in request.FILES:
                    ProductImage.objects.create(
                        product=product,
                        image=request.FILES['primary_image'],
                        is_primary=True,
                        alt_text=product.name,
                    )
                for idx, extra_file in enumerate(request.FILES.getlist('extra_images'), start=1):
                    ProductImage.objects.create(
                        product=product,
                        image=extra_file,
                        is_primary=(not product.images.exists()),
                        order=idx,
                        alt_text=product.name,
                    )
                messages.success(request, f"Produit « {product.name} » publié avec succès !")
                if request.POST.get('save_and_add') == '1':
                    return redirect('backoffice:product_create')
                return redirect('backoffice:products')
    else:
        form = ProductForm()

    return render(request, 'backoffice/product_form.html', {
        'form': form,
        'title': 'Nouveau Produit',
        'current_page': 'products',
    })


@staff_required
def product_edit_view(request, product_id):
    """Modification complète d'un produit existant (avec découpe 15s & compression 8 Mo auto)."""
    from django.core.exceptions import ValidationError
    from shop.video_utils import process_uploaded_product_video

    product = get_object_or_404(Product.objects.prefetch_related('images'), id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = form.cleaned_data['category']
            product.brand = form.cleaned_data.get('brand')
            product.description = form.cleaned_data['description']
            if not product.addon_price:
                product.addon_price = 0

            raw_specs = (request.POST.get('specifications_json') or '').strip()
            if raw_specs:
                import json
                try:
                    parsed_specs = json.loads(raw_specs)
                    if isinstance(parsed_specs, dict):
                        product.specifications = parsed_specs
                except Exception:
                    pass
            if request.POST.get('remove_video') == '1' and product.video_file:
                product.video_file.delete(save=False)
                product.video_file = None

            video_ok = True
            if 'video_file' in request.FILES:
                try:
                    processed_video, v_info = process_uploaded_product_video(request.FILES['video_file'])
                    product.video_file = processed_video
                    if v_info.get('summary'):
                        messages.info(request, v_info['summary'])
                except ValidationError as ve:
                    video_ok = False
                    err_txt = ve.messages[0] if hasattr(ve, 'messages') and ve.messages else str(ve)
                    form.add_error(None, err_txt)
                    messages.error(request, err_txt)

            if video_ok:
                product.save()
                try:
                    from django.core.cache import cache
                    cache.delete('menu_categories_cached')
                except Exception:
                    pass
                if 'primary_image' in request.FILES:
                    primary = product.images.filter(is_primary=True).first()
                    if primary:
                        primary.image = request.FILES['primary_image']
                        primary.save()
                    else:
                        ProductImage.objects.create(
                            product=product,
                            image=request.FILES['primary_image'],
                            is_primary=True,
                            alt_text=product.name,
                        )
                for idx, extra_file in enumerate(request.FILES.getlist('extra_images'), start=1):
                    ProductImage.objects.create(
                        product=product,
                        image=extra_file,
                        is_primary=False,
                        order=product.images.count() + idx,
                        alt_text=product.name,
                    )
                messages.success(request, f"Produit « {product.name} » mis à jour.")
                return redirect('backoffice:products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'backoffice/product_form.html', {
        'form': form,
        'product': product,
        'title': product.name,
        'current_page': 'products',
    })


@staff_required
@require_POST
def product_video_compress_api_view(request):
    """
    Endpoint AJAX de compression & découpe vidéo (max 15s, max 8 Mo) en direct depuis le formulaire produit.
    Retourne le flux MP4 compressé en base64 ou métadonnées pour prévisualisation instantanée.
    """
    import base64
    from django.http import JsonResponse
    from django.core.exceptions import ValidationError
    from shop.video_utils import process_uploaded_product_video

    video_file = request.FILES.get('video_file')
    if not video_file:
        return JsonResponse({'status': 'error', 'message': 'Aucun fichier vidéo fourni.'}, status=400)

    try:
        processed, info = process_uploaded_product_video(video_file)
        if hasattr(processed, 'seek'):
            processed.seek(0)
        raw_bytes = processed.read()
        b64_data = base64.b64encode(raw_bytes).decode('ascii')
        return JsonResponse({
            'status': 'ok',
            'filename': getattr(processed, 'name', 'video_15s.mp4'),
            'content_type': 'video/mp4',
            'size_bytes': len(raw_bytes),
            'size_mb': round(len(raw_bytes) / (1024 * 1024), 2),
            'duration': info.get('final_duration') or 15.0,
            'was_trimmed': info.get('was_trimmed', False),
            'was_compressed': info.get('was_compressed', False),
            'summary': info.get('summary') or 'Vidéo optimisée (≤ 15s et ≤ 8 Mo).',
            'base64': b64_data,
        })
    except ValidationError as ve:
        msg = ve.messages[0] if hasattr(ve, 'messages') and ve.messages else str(ve)
        return JsonResponse({'status': 'error', 'message': msg}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f"Erreur compression : {str(e)}"}, status=500)


@staff_required
@require_POST
def product_quick_update_view(request, product_id):
    """Mise à jour express du prix d'achat, prix vente, prix promo, stock et mise en avant."""
    product = get_object_or_404(Product, id=product_id)
    try:
        raw_cost = (request.POST.get('cost_price') or '').strip()
        if raw_cost == '':
            product.cost_price = None
        else:
            cost_val = int(float(raw_cost))
            product.cost_price = cost_val if cost_val >= 0 else None

        raw_price = (request.POST.get('price') or '').strip()
        if raw_price:
            product.price = max(0, int(float(raw_price)))

        raw_sale = (request.POST.get('sale_price') or '').strip()
        if raw_sale == '':
            product.sale_price = None
        else:
            sale_val = int(float(raw_sale))
            product.sale_price = sale_val if sale_val > 0 else None

        raw_stock = (request.POST.get('stock') or '').strip()
        if raw_stock != '':
            product.stock = max(0, int(float(raw_stock)))
            if product.track_stock:
                product.status = Product.Status.ACTIVE if product.stock > 0 else Product.Status.OUT_OF_STOCK

        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()
        messages.success(request, f"« {product.name} » mis à jour ({int(product.current_price):,} FCFA • Stock: {product.stock}).".replace(',', ' '))
    except Exception:
        messages.error(request, "Valeurs numériques invalides.")

    next_url = request.POST.get('next') or ''
    if next_url.startswith('/gestion/'):
        return redirect(next_url)
    return redirect('backoffice:products')


@staff_required
@require_POST
def product_delete_view(request, product_id):
    """Suppression d'un produit depuis la fiche ou la liste."""
    product = get_object_or_404(Product, id=product_id)
    pname = product.name
    product.delete()
    try:
        from django.core.cache import cache
        cache.delete('menu_categories_cached')
    except Exception:
        pass
    messages.success(request, f"L'article « {pname} » a été supprimé du catalogue.")
    return redirect('backoffice:products')


@staff_required
@require_POST
def product_set_primary_image_view(request, product_id, image_id):
    """Définir une photo secondaire comme photo principale du produit en 1 clic."""
    product = get_object_or_404(Product, id=product_id)
    img = get_object_or_404(ProductImage, id=image_id, product=product)
    ProductImage.objects.filter(product=product).update(is_primary=False)
    img.is_primary = True
    img.order = 0
    img.save(update_fields=['is_primary', 'order'])
    messages.success(request, "Photo principale mise à jour.")
    return redirect('backoffice:product_edit', product_id=product.id)


@staff_required
@require_POST
def product_delete_image_view(request, product_id, image_id):
    """Supprimer une photo secondaire d'un produit."""
    product = get_object_or_404(Product, id=product_id)
    img = get_object_or_404(ProductImage, id=image_id, product=product)
    was_primary = img.is_primary
    img.delete()
    if was_primary:
        nxt = product.images.first()
        if nxt:
            nxt.is_primary = True
            nxt.save(update_fields=['is_primary'])
    messages.success(request, "Photo supprimée.")
    return redirect('backoffice:product_edit', product_id=product.id)


@staff_required
@require_POST  # Sécurité + anti-pattern : rendu via template, plus de HTML dans Python
def product_toggle_active_htmx(request, product_id):
    """Activer ou désactiver un produit via HTMX — POST uniquement, rendu par partial."""
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    return render(request, 'backoffice/partials/product_active_toggle.html', {'product': product})


# ---------------------------------------------------------------------------
# Mode Tableur Excel & Gestion en Masse (Bulk Edit / Create / Actions)
# ---------------------------------------------------------------------------

@staff_required
def products_bulk_edit_view(request):
    """Mode Tableur Excel : modification instantanée en masse des prix, promos, stocks et statuts."""
    category_slug = request.GET.get('category', '')
    brand_id = request.GET.get('brand', '')
    stock_status = request.GET.get('stock', '')
    search_query = request.GET.get('q', '').strip()
    try:
        per_page = int(request.GET.get('per_page', 50))
    except ValueError:
        per_page = 50

    products_qs = (
        Product.objects
        .select_related('category', 'brand')
        .prefetch_related('images')
        .order_by('-created_at')
    )

    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)
    if brand_id:
        products_qs = products_qs.filter(brand_id=brand_id)
    if stock_status == 'low':
        products_qs = products_qs.filter(track_stock=True, stock__lte=F('min_stock'), stock__gt=0)
    elif stock_status == 'out':
        products_qs = products_qs.filter(track_stock=True, stock=0)
    elif stock_status == 'featured':
        products_qs = products_qs.filter(is_featured=True)
    elif stock_status == 'inactive':
        products_qs = products_qs.filter(is_active=False)

    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    total_filtered_count = products_qs.count()
    paginator = Paginator(products_qs, min(max(per_page, 20), 200))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_brand': brand_id,
        'selected_stock': stock_status,
        'total_filtered_count': total_filtered_count,
        'total_products_count': Product.objects.count(),
        'per_page': per_page,
        'current_page': 'products',
    }
    return render(request, 'backoffice/products_bulk_edit.html', context)


@staff_required
@require_POST
def products_bulk_save_view(request):
    """Enregistre en bloc toutes les modifications du tableur Excel (prix, stocks, statuts)."""
    import json
    from django.db import transaction
    from django.http import JsonResponse
    
    updated_count = 0

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body)
            items = payload.get('items', [])
        else:
            raw_json = request.POST.get('bulk_items_json')
            items = json.loads(raw_json) if raw_json else []

        if not items:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'warning', 'message': 'Aucune modification à enregistrer.'})
            messages.warning(request, "Aucune modification détectée.")
            return redirect('backoffice:products_bulk_edit')

        with transaction.atomic():
            for item in items:
                p_id = item.get('id')
                if not p_id:
                    continue
                try:
                    product = Product.objects.select_for_update().get(id=p_id)
                except Product.DoesNotExist:
                    continue

                dirty = False
                if 'name' in item and str(item['name']).strip():
                    new_name = str(item['name']).strip()
                    if product.name != new_name:
                        product.name = new_name
                        dirty = True

                if 'cost_price' in item:
                    val = item['cost_price']
                    new_cost = int(float(val)) if (val is not None and str(val).strip() != '') else None
                    if new_cost is not None and new_cost < 0:
                        new_cost = None
                    if product.cost_price != new_cost:
                        product.cost_price = new_cost
                        dirty = True

                if 'price' in item and str(item['price']).strip() != '':
                    new_price = max(0, int(float(item['price'])))
                    if product.price != new_price:
                        product.price = new_price
                        dirty = True

                if 'sale_price' in item:
                    val = item['sale_price']
                    new_sale = int(float(val)) if (val is not None and str(val).strip() != '') else None
                    if new_sale is not None and new_sale <= 0:
                        new_sale = None
                    if product.sale_price != new_sale:
                        product.sale_price = new_sale
                        dirty = True

                if 'stock' in item and str(item['stock']).strip() != '':
                    new_stock = max(0, int(float(item['stock'])))
                    if product.stock != new_stock:
                        product.stock = new_stock
                        if product.track_stock:
                            product.status = Product.Status.ACTIVE if product.stock > 0 else Product.Status.OUT_OF_STOCK
                        dirty = True

                if 'min_stock' in item and str(item['min_stock']).strip() != '':
                    new_min = max(0, int(float(item['min_stock'])))
                    if product.min_stock != new_min:
                        product.min_stock = new_min
                        dirty = True

                if 'category_id' in item and item['category_id']:
                    try:
                        cat_id = int(item['category_id'])
                        if product.category_id != cat_id:
                            product.category_id = cat_id
                            dirty = True
                    except (ValueError, TypeError):
                        pass

                if 'brand_id' in item:
                    try:
                        b_id = int(item['brand_id']) if item['brand_id'] else None
                        if product.brand_id != b_id:
                            product.brand_id = b_id
                            dirty = True
                    except (ValueError, TypeError):
                        pass

                if 'is_featured' in item:
                    feat = bool(item['is_featured'])
                    if product.is_featured != feat:
                        product.is_featured = feat
                        dirty = True

                if 'is_active' in item:
                    act = bool(item['is_active'])
                    if product.is_active != act:
                        product.is_active = act
                        dirty = True

                if dirty:
                    product.save()
                    updated_count += 1

        msg = f"✓ {updated_count} produit{'s' if updated_count > 1 else ''} mis à jour avec succès !"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'ok', 'updated_count': updated_count, 'message': msg})

        messages.success(request, msg)
    except Exception as e:
        err_msg = f"Erreur lors de la sauvegarde : {str(e)}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        messages.error(request, err_msg)

    return redirect('backoffice:products_bulk_edit')


@staff_required
@require_POST
def products_bulk_action_view(request):
    """Applique une action groupée sur les produits sélectionnés (stock, remise, activation, etc.)."""
    from django.db import transaction

    action = request.POST.get('bulk_action', '').strip()
    selected_ids = request.POST.getlist('selected_ids')

    if not selected_ids:
        raw_ids = request.POST.get('selected_ids_str', '')
        if raw_ids:
            selected_ids = [x.strip() for x in raw_ids.split(',') if x.strip()]

    if not selected_ids:
        messages.warning(request, "Veuillez cocher au moins un produit pour appliquer une action groupée.")
        return redirect(request.META.get('HTTP_REFERER') or 'backoffice:products_bulk_edit')

    products = Product.objects.filter(id__in=selected_ids)
    count = products.count()

    with transaction.atomic():
        if action == 'add_stock':
            try:
                delta = int(request.POST.get('stock_delta', 0))
                for p in products:
                    p.stock = max(0, p.stock + delta)
                    if p.track_stock:
                        p.status = Product.Status.ACTIVE if p.stock > 0 else Product.Status.OUT_OF_STOCK
                    p.save(update_fields=['stock', 'status'])
                messages.success(request, f"Stock ajusté (+{delta}) sur {count} produit(s).")
            except ValueError:
                messages.error(request, "Quantité de stock invalide.")

        elif action == 'set_stock':
            try:
                val = max(0, int(request.POST.get('stock_value', 0)))
                for p in products:
                    p.stock = val
                    if p.track_stock:
                        p.status = Product.Status.ACTIVE if p.stock > 0 else Product.Status.OUT_OF_STOCK
                    p.save(update_fields=['stock', 'status'])
                messages.success(request, f"Stock défini à {val} unités sur {count} produit(s).")
            except ValueError:
                messages.error(request, "Valeur de stock invalide.")

        elif action == 'discount_pct':
            try:
                pct = max(1, min(90, float(request.POST.get('discount_pct', 10))))
                for p in products:
                    p.sale_price = int(p.price * (1 - pct / 100))
                    p.save(update_fields=['sale_price'])
                messages.success(request, f"Remise de {pct}% appliquée sur {count} produit(s).")
            except ValueError:
                messages.error(request, "Pourcentage de remise invalide.")

        elif action == 'remove_discount':
            products.update(sale_price=None)
            messages.success(request, f"Prix promos retirés sur {count} produit(s).")

        elif action == 'activate':
            products.update(is_active=True)
            messages.success(request, f"{count} produit(s) activé(s) sur la boutique.")

        elif action == 'deactivate':
            products.update(is_active=False)
            messages.success(request, f"{count} produit(s) désactivé(s) / masqué(s).")

        elif action == 'feature':
            products.update(is_featured=True)
            messages.success(request, f"{count} produit(s) mis en vedette.")

        elif action == 'unfeature':
            products.update(is_featured=False)
            messages.success(request, f"{count} produit(s) retiré(s) des vedettes.")

        elif action == 'delete':
            deleted_count, _ = products.delete()
            messages.success(request, f"{count} produit(s) supprimé(s) définitivement.")

    return redirect(request.META.get('HTTP_REFERER') or 'backoffice:products_bulk_edit')


@staff_required
def products_bulk_create_view(request):
    """Ajout rapide de produits en masse sous forme de grille Excel (Nom, Prix, Stock, Image)."""
    from django.db import transaction

    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        row_count = int(request.POST.get('row_count', 10))
        created_count = 0

        with transaction.atomic():
            for i in range(row_count):
                name = (request.POST.get(f'name_{i}') or '').strip()
                if not name:
                    continue

                cat_id = request.POST.get(f'category_{i}')
                brand_id = request.POST.get(f'brand_{i}')
                raw_cost = request.POST.get(f'cost_price_{i}', '').strip()
                raw_price = request.POST.get(f'price_{i}', '0').strip()
                raw_sale = request.POST.get(f'sale_price_{i}', '').strip()
                raw_stock = request.POST.get(f'stock_{i}', '0').strip()
                sku = (request.POST.get(f'sku_{i}') or '').strip()

                try:
                    cost_price = int(float(raw_cost)) if raw_cost else None
                except ValueError:
                    cost_price = None

                try:
                    price = max(0, int(float(raw_price)))
                except ValueError:
                    price = 0

                try:
                    sale_price = int(float(raw_sale)) if raw_sale else None
                except ValueError:
                    sale_price = None

                try:
                    stock = max(0, int(float(raw_stock)))
                except ValueError:
                    stock = 0

                cat = Category.objects.filter(id=cat_id).first() if cat_id else categories.first()
                brand = Brand.objects.filter(id=brand_id).first() if brand_id else None

                base_slug = slugify(name) or 'produit'
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                product = Product.objects.create(
                    name=name,
                    slug=slug,
                    category=cat,
                    brand=brand,
                    cost_price=cost_price,
                    price=price,
                    sale_price=sale_price,
                    stock=stock,
                    min_stock=2,
                    track_stock=True,
                    sku=sku or '',
                    is_active=True,
                    short_description=f"{name} — Disponible chez Onizuka Shop au Grand Marché de Bamako (Dibidani).",
                    description=f"{name} — Disponible chez Onizuka Shop au Grand Marché de Bamako (Dibidani) avec garantie officielle et livraison 24h.",
                )

                img_file = request.FILES.get(f'image_{i}')
                if img_file:
                    ProductImage.objects.create(
                        product=product,
                        image=img_file,
                        is_primary=True,
                        alt_text=name
                    )

                created_count += 1

        if created_count > 0:
            messages.success(request, f"🎉 {created_count} nouveaux produits ajoutés au catalogue avec succès !")
            return redirect('backoffice:products_bulk_edit')
        else:
            messages.warning(request, "Aucun produit renseigné. Veuillez remplir au moins un nom.")

    return render(request, 'backoffice/products_bulk_create.html', {
        'categories': categories,
        'brands': brands,
        'initial_rows': range(8),
        'current_page': 'products',
    })


@staff_required
@require_POST
def product_quick_image_upload_view(request, product_id):
    """Téléversement instantané d'une photo pour une ligne du tableur Excel."""
    from django.http import JsonResponse

    product = get_object_or_404(Product, id=product_id)
    img_file = request.FILES.get('image')
    if not img_file:
        return JsonResponse({'status': 'error', 'message': 'Aucun fichier reçu.'}, status=400)

    try:
        ProductImage.objects.filter(product=product).update(is_primary=False)
        img = ProductImage.objects.create(
            product=product,
            image=img_file,
            is_primary=True,
            alt_text=product.name
        )
        url = img.thumbnail.url if hasattr(img, 'thumbnail') and img.thumbnail else img.image.url
        return JsonResponse({'status': 'ok', 'url': url, 'message': 'Photo enregistrée !'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ---------------------------------------------------------------------------
# Stocks & Réapprovisionnement
# ---------------------------------------------------------------------------

@staff_required
def stocks_view(request):
    """Gestion des stocks, alertes réapprovisionnement et entrées de marchandises."""
    supply_form = StockSupplyForm()
    form_has_errors = False

    if request.method == 'POST':
        supply_form = StockSupplyForm(request.POST)
        if supply_form.is_valid():
            product_id = supply_form.cleaned_data['product_id']
            qty = supply_form.cleaned_data['quantity']
            supplier = supply_form.cleaned_data['supplier']
            reference = supply_form.cleaned_data['reference']
            notes = supply_form.cleaned_data['notes']

            product = get_object_or_404(Product, id=product_id)
            stock_before = product.stock
            product.stock += qty
            if product.stock > 0 and product.status == Product.Status.OUT_OF_STOCK:
                product.status = Product.Status.ACTIVE
            product.save(update_fields=['stock', 'status'])

            StockMovement.objects.create(
                product=product,
                movement_type=StockMovement.MovementType.IN,
                quantity=qty,
                stock_before=stock_before,
                stock_after=product.stock,
                supplier=supplier,
                reference=reference,
                notes=notes,
                created_by=request.user,
            )
            messages.success(
                request,
                f"Stock approvisionné : +{qty} unités pour « {product.name} ». Nouveau stock : {product.stock}.",
            )
            return redirect('backoffice:stocks')
        else:
            # Formulaire invalide : rouvrir le modal avec les erreurs visibles
            form_has_errors = True
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire d'approvisionnement.")

    filter_urgency = request.GET.get('filter', 'all')
    search_q = request.GET.get('q', '').strip()

    products_qs = (
        Product.objects
        .filter(track_stock=True)
        .select_related('category', 'brand')
        .order_by('stock')
    )

    if filter_urgency == 'out':
        products_qs = products_qs.filter(stock=0)
    elif filter_urgency == 'low':
        products_qs = products_qs.filter(stock__lte=F('min_stock'), stock__gt=0)
    elif filter_urgency == 'critical':
        products_qs = products_qs.filter(stock__lte=F('min_stock'))

    if search_q:
        products_qs = products_qs.filter(
            Q(name__icontains=search_q) |
            Q(sku__icontains=search_q) |
            Q(brand__name__icontains=search_q)
        )

    # Chiffres globaux : UNE seule requête annotée au lieu de 3 COUNT séparés
    stock_agg = Product.objects.filter(track_stock=True).aggregate(
        total=Count('id'),
        out=Count('id', filter=Q(stock=0)),
        low=Count('id', filter=Q(stock__lte=F('min_stock'), stock__gt=0)),
    )
    total_tracked_products = stock_agg['total'] or 0
    out_of_stock_count = stock_agg['out'] or 0
    low_stock_count = stock_agg['low'] or 0

    recent_movements = (
        StockMovement.objects
        .select_related('product', 'supplier', 'created_by')
        .order_by('-created_at')[:15]
    )
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    all_products_select = Product.objects.filter(track_stock=True).only('id', 'name', 'sku', 'stock').order_by('name')

    paginator = Paginator(products_qs, 20)
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'all_products_select': all_products_select,
        'filter_urgency': filter_urgency,
        'search_q': search_q,
        'total_tracked_products': total_tracked_products,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
        'recent_movements': recent_movements,
        'suppliers': suppliers,
        'supply_form': supply_form,
        'form_has_errors': form_has_errors,
        'current_page': 'stocks',
    }
    return render(request, 'backoffice/stocks.html', context)


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

@staff_required
def clients_view(request):
    """Annuaire des clients, volumes d'achat et adresses de livraison."""
    search_query = request.GET.get('q', '').strip()

    # Calcul du total AVANT le filtre de recherche, sans prefetch inutile
    clients_base_qs = User.objects.filter(is_staff=False, is_superuser=False)
    total_clients_count = clients_base_qs.count()

    # prefetch 'orders' retiré : bombe mémoire pour 1000+ clients avec beaucoup de commandes
    clients_qs = (
        clients_base_qs
        .select_related('profile')
        .prefetch_related('addresses')
        .order_by('-date_joined')
    )

    if search_query:
        clients_qs = clients_qs.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__phone__icontains=search_query)
        )

    paginator = Paginator(clients_qs, 20)
    page_number = request.GET.get('page', 1)
    clients = paginator.get_page(page_number)

    context = {
        'clients': clients,
        'search_query': search_query,
        'total_clients_count': total_clients_count,
        'current_page': 'clients',
    }
    return render(request, 'backoffice/clients_list.html', context)


@staff_required
def client_detail_view(request, client_id):
    """Fiche détaillée d'un client avec adresses à Bamako et historique d'achats."""
    client = get_object_or_404(
        User.objects.select_related('profile'),
        id=client_id,
        is_staff=False,
        is_superuser=False,
    )
    orders = client.orders.order_by('-created_at')
    addresses = client.addresses.all()

    total_spent = (
        orders
        .exclude(status__in=[Order.Status.CANCELLED, Order.Status.REFUNDED])
        .aggregate(total=Sum('total'))['total'] or 0
    )

    context = {
        'client': client,
        'orders': orders,
        'addresses': addresses,
        'total_spent': total_spent,
        'orders_count': orders.count(),
        'current_page': 'clients',
    }
    return render(request, 'backoffice/client_detail.html', context)


# ---------------------------------------------------------------------------
# Paramètres & Configuration Générale de l'Entreprise
# ---------------------------------------------------------------------------

@staff_required
def settings_view(request):
    """Configuration générale de la boutique, logistique Bamako et identité société."""
    from .models import ShopSetting
    from .forms import ShopSettingForm

    settings_obj = ShopSetting.get_settings()

    if request.method == 'POST':
        form = ShopSettingForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            try:
                from django.core.cache import cache
                cache.delete('shop_settings_cached')
            except Exception:
                pass
            messages.success(request, "Les paramètres de la boutique et de l'entreprise ont été enregistrés avec succès.")
            return redirect('backoffice:settings')
        else:
            messages.error(request, "Veuillez vérifier les informations renseignées.")
    else:
        form = ShopSettingForm(instance=settings_obj)

    context = {
        'form': form,
        'settings': settings_obj,
        'current_page': 'settings',
    }
    return render(request, 'backoffice/settings.html', context)


# ---------------------------------------------------------------------------
# Gestion des Utilisateurs & Équipe
# ---------------------------------------------------------------------------

@staff_required
def users_view(request):
    """Gestion des comptes utilisateurs, direction, staff et clients."""
    from .forms import UserCreateForm

    search_query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', 'all')

    users_qs = User.objects.select_related('profile').order_by('-date_joined')

    # Si l'utilisateur connecté n'est pas le superuser dev, masquer strictement les superutilisateurs
    if not request.user.is_superuser:
        users_qs = users_qs.filter(is_superuser=False)
        total_count = User.objects.filter(is_superuser=False).count()
        staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
    else:
        total_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()

    if role_filter == 'staff':
        users_qs = users_qs.filter(is_staff=True)
    elif role_filter == 'clients':
        users_qs = users_qs.filter(is_staff=False, is_superuser=False)
    elif role_filter == 'superusers':
        if request.user.is_superuser:
            users_qs = users_qs.filter(is_superuser=True)
        else:
            users_qs = users_qs.none()

    if search_query:
        users_qs = users_qs.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__phone__icontains=search_query)
        )

    clients_count = User.objects.filter(is_staff=False, is_superuser=False).count()

    paginator = Paginator(users_qs, 25)
    page_number = request.GET.get('page', 1)
    users = paginator.get_page(page_number)

    create_form = UserCreateForm()

    context = {
        'users': users,
        'create_form': create_form,
        'search_query': search_query,
        'role_filter': role_filter,
        'total_count': total_count,
        'staff_count': staff_count,
        'clients_count': clients_count,
        'current_page': 'users',
    }
    return render(request, 'backoffice/users_list.html', context)


@staff_required
def user_create_view(request):
    """Création rapide d'un membre d'équipe ou client."""
    from .forms import UserCreateForm
    from accounts.models import Profile

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            phone = form.cleaned_data.get('phone', '')
            role = form.cleaned_data['role']

            if User.objects.filter(username=username).exists():
                messages.error(request, f"L'identifiant « {username} » est déjà utilisé.")
                return redirect('backoffice:users')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            if role == 'direction':
                user.is_staff = True
                user.is_superuser = True if request.user.is_superuser else False
            elif role == 'gestionnaire':
                user.is_staff = True
                user.is_superuser = False
            else:
                user.is_staff = False
                user.is_superuser = False
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            if phone:
                profile.phone = phone
                profile.save()

            messages.success(request, f"Le compte de « {user.get_full_name() or user.username} » a été créé avec succès.")
        else:
            messages.error(request, "Erreur dans les champs du formulaire de création.")

    return redirect('backoffice:users')


@staff_required
@require_POST
def user_toggle_status_view(request, user_id):
    """Activer ou désactiver l'accès d'un compte utilisateur."""
    user_target = get_object_or_404(User, id=user_id)

    # Protection stricte : les membres de direction ne peuvent pas toucher au compte superuser dev
    if user_target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Action non autorisée sur ce compte.")
        return redirect('backoffice:users')

    if user_target.id == request.user.id:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte d'administrateur.")
        return redirect('backoffice:users')

    user_target.is_active = not user_target.is_active
    user_target.save(update_fields=['is_active'])
    status_str = "activé" if user_target.is_active else "suspendu"
    messages.success(request, f"Le compte de {user_target.username} a été {status_str}.")
    return redirect('backoffice:users')


@staff_required
@require_POST
def user_edit_role_view(request, user_id):
    """Modifier le rôle et les informations de contact d'un utilisateur par la Direction."""
    from .forms import UserEditRoleForm
    from accounts.models import Profile

    user_target = get_object_or_404(User, id=user_id)

    # Protection superadmin : un staff ordinaire ne peut pas modifier un superadmin
    if user_target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Action non autorisée sur ce compte super-administrateur.")
        return redirect('backoffice:users')

    form = UserEditRoleForm(request.POST, is_superuser=request.user.is_superuser)
    if form.is_valid():
        first_name = form.cleaned_data.get('first_name', '')
        last_name = form.cleaned_data.get('last_name', '')
        email = form.cleaned_data.get('email', '')
        phone = form.cleaned_data.get('phone', '')
        role = form.cleaned_data.get('role')

        # Empêcher l'administrateur connecté de se rétrograder lui-même
        if user_target.id == request.user.id and role == 'client':
            messages.error(request, "Vous ne pouvez pas révoquer vos propres droits d'administrateur.")
            return redirect('backoffice:users')

        user_target.first_name = first_name
        user_target.last_name = last_name
        user_target.email = email

        if role == 'direction' and request.user.is_superuser:
            user_target.is_staff = True
            user_target.is_superuser = True
        elif role == 'gestionnaire':
            user_target.is_staff = True
            user_target.is_superuser = False
        else:  # client
            user_target.is_staff = False
            user_target.is_superuser = False

        user_target.save()

        profile, _ = Profile.objects.get_or_create(user=user_target)
        if phone is not None:
            profile.phone = phone
            profile.save()

        role_display = "Gestionnaire Direction" if user_target.is_staff else "Client Acheteur"
        if user_target.is_superuser:
            role_display = "Super-Administrateur"
        messages.success(request, f"Le compte de {user_target.username} a été mis à jour avec succès (Rôle : {role_display}).")
    else:
        messages.error(request, "Erreur lors de la mise à jour du rôle utilisateur.")

    return redirect('backoffice:users')



@staff_required
def export_orders_csv_view(request):
    """Exporter les commandes en format CSV pour la comptabilité et gestion."""
    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"commandes_onizouka_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # BOM pour compatibilité Excel
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Reference',
        'Date_Commande',
        'Nom_Client',
        'Telephone',
        'Email',
        'Quartier_Ville',
        'Methode_Paiement',
        'Statut_Paiement',
        'Statut_Commande',
        'Sous_Total_FCFA',
        'Livraison_FCFA',
        'Total_FCFA',
        'Nb_Articles',
    ])

    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    for order in orders:
        client_name = order.delivery_name or (order.user.get_full_name() if order.user else 'Client Anonyme')
        phone = order.delivery_phone or ''
        email = order.user.email if order.user else ''
        district = f"{order.delivery_district}, {order.delivery_city}".strip(', ')
        
        writer.writerow([
            order.order_number,
            order.created_at.strftime("%d/%m/%Y %H:%M"),
            client_name,
            phone,
            email,
            district,
            order.get_payment_method_display(),
            "Payé" if order.payment_status else "En attente",
            order.get_status_display(),
            int(order.subtotal or 0),
            int(order.delivery_fee or 0),
            int(order.total or 0),
            order.items.count(),
        ])

    return response


@staff_required
def export_products_csv_view(request):
    """Exporter tout le catalogue de produits en format CSV (compatible Excel Bamako/Mali)."""
    timestamp = timezone.now().strftime("%Y%m%d_%H%M")
    filename = f"catalogue_produits_onizouka_{timestamp}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # BOM UTF-8 pour ouverture directe dans Excel sans problème d'accents
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'SKU',
        'Nom_Produit',
        'Categorie',
        'Marque',
        'Prix_Vente_FCFA',
        'Prix_Promo_FCFA',
        'Prix_Revient_FCFA',
        'Stock',
        'Stock_Minimum',
        'Statut',
        'Visible',
        'En_Vedette',
        'Nouveau',
        'Description_Courte',
    ])

    products = Product.objects.select_related('category', 'brand').order_by('category__name', 'name')

    for p in products:
        writer.writerow([
            p.sku or '',
            p.name,
            p.category.name if p.category else '',
            p.brand.name if p.brand else '',
            int(p.price) if p.price is not None else 0,
            int(p.sale_price) if p.sale_price is not None else '',
            int(p.cost_price) if p.cost_price is not None else '',
            p.stock,
            p.min_stock,
            p.status,
            'OUI' if p.is_active else 'NON',
            'OUI' if p.is_featured else 'NON',
            'OUI' if p.is_new else 'NON',
            (p.short_description or '').replace('\n', ' ').strip(),
        ])

    return response


@staff_required
def download_product_template_csv_view(request):
    """Télécharger le modèle CSV officiel pour l'import en masse de produits."""
    filename = "modele_import_produits_onizouka.csv"
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'SKU',
        'Nom_Produit',
        'Categorie',
        'Marque',
        'Prix_Vente_FCFA',
        'Prix_Promo_FCFA',
        'Prix_Revient_FCFA',
        'Stock',
        'Stock_Minimum',
        'Statut',
        'Visible',
        'En_Vedette',
        'Nouveau',
        'Description_Courte',
    ])

    # Exemples types représentatifs du magasin Onizouka Dibidani
    writer.writerow([
        'ONZ-REF-SAM-385',
        'Réfrigérateur Combiné Samsung 385L NoFrost Digital Inverter',
        'Réfrigérateurs',
        'Samsung',
        '450000',
        '425000',
        '360000',
        '12',
        '3',
        'active',
        'OUI',
        'OUI',
        'NON',
        'Capacité 385L, All-Around Cooling, compresseur Digital Inverter garanti 10 ans.',
    ])
    writer.writerow([
        'ONZ-CLM-HAI-12K',
        'Climatiseur Split Haier 12000 BTU R410A Tropicalisé',
        'Climatiseurs',
        'Haier',
        '245000',
        '',
        '195000',
        '25',
        '5',
        'active',
        'OUI',
        'NON',
        'OUI',
        'Refroidissement ultra-rapide, conçu pour les fortes chaleurs de Bamako.',
    ])

    return response


@staff_required
@require_POST
def import_products_csv_view(request):
    """Importer ou mettre à jour en masse des produits depuis un fichier CSV."""
    if 'csv_file' not in request.FILES:
        messages.error(request, "Veuillez sélectionner un fichier CSV à importer.")
        return redirect('backoffice:products')

    csv_file = request.FILES['csv_file']
    if not csv_file.name.endswith(('.csv', '.txt')):
        messages.error(request, "Format de fichier non valide. Veuillez importer un fichier .csv")
        return redirect('backoffice:products')

    try:
        content = csv_file.read()
        # Décodage intelligent (UTF-8 avec ou sans BOM, ou ISO-8859-1 / cp1252)
        try:
            decoded = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                decoded = content.decode('latin-1')
            except UnicodeDecodeError:
                decoded = content.decode('cp1252', errors='replace')

        # Détection du délimiteur (; ou ,)
        lines = decoded.splitlines()
        if not lines:
            messages.warning(request, "Le fichier CSV importé est vide.")
            return redirect('backoffice:products')

        first_line = lines[0]
        delimiter = ';' if ';' in first_line else ','

        reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Normaliser les clés d'en-tête (enlever espaces, minuscules, etc.)
        def clean_key(key):
            if not key:
                return ''
            k = key.strip().lower().replace(' ', '_').replace('é', 'e').replace('è', 'e').replace('ê', 'e')
            return k

        # Pré-chargement des catégories et marques existantes pour optimiser
        categories_cache = {c.name.lower(): c for c in Category.objects.all()}
        brands_cache = {b.name.lower(): b for b in Brand.objects.all()}

        # Catégorie par défaut si non précisée
        default_cat = Category.objects.filter(is_active=True).first()
        if not default_cat:
            default_cat = Category.objects.create(name="Électronique", slug="electronique")
            categories_cache["électronique"] = default_cat

        for row_idx, raw_row in enumerate(reader, start=2):
            row = {clean_key(k): (v.strip() if v else '') for k, v in raw_row.items() if k}

            sku = row.get('sku', '').strip()
            name = row.get('nom_produit', '') or row.get('nom', '') or row.get('name', '')

            if not name:
                skipped_count += 1
                continue

            # Traitement Catégorie
            cat_name = row.get('categorie', '') or row.get('category', '')
            category = None
            if cat_name:
                cat_lower = cat_name.lower()
                if cat_lower in categories_cache:
                    category = categories_cache[cat_lower]
                else:
                    cat_slug = slugify(cat_name)
                    category, _ = Category.objects.get_or_create(
                        slug=cat_slug,
                        defaults={'name': cat_name}
                    )
                    categories_cache[cat_lower] = category
            if not category:
                category = default_cat

            # Traitement Marque
            brand_name = row.get('marque', '') or row.get('brand', '')
            brand = None
            if brand_name:
                brand_lower = brand_name.lower()
                if brand_lower in brands_cache:
                    brand = brands_cache[brand_lower]
                else:
                    brand_slug = slugify(brand_name)
                    brand, _ = Brand.objects.get_or_create(
                        slug=brand_slug,
                        defaults={'name': brand_name}
                    )
                    brands_cache[brand_lower] = brand

            # Nettoyage des prix (enlever espaces, 'FCFA', etc.)
            def parse_int(val, default=0):
                if not val:
                    return default
                cleaned = ''.join(c for c in str(val) if c.isdigit())
                return int(cleaned) if cleaned else default

            price = parse_int(row.get('prix_vente_fcfa', '') or row.get('prix', '') or row.get('price', ''), 0)
            sale_price_raw = row.get('prix_promo_fcfa', '') or row.get('prix_promo', '') or row.get('sale_price', '')
            sale_price = parse_int(sale_price_raw, None) if sale_price_raw else None
            cost_price_raw = row.get('prix_revient_fcfa', '') or row.get('prix_revient', '') or row.get('cost_price', '')
            cost_price = parse_int(cost_price_raw, None) if cost_price_raw else None

            stock = parse_int(row.get('stock', ''), 0)
            min_stock = parse_int(row.get('stock_minimum', '') or row.get('min_stock', ''), 5)

            status = row.get('statut', '') or Product.Status.ACTIVE
            if status not in [choice[0] for choice in Product.Status.choices]:
                status = Product.Status.ACTIVE

            def parse_bool(val, default=True):
                if not val:
                    return default
                v = str(val).strip().upper()
                return v in ['OUI', '1', 'TRUE', 'VRAI', 'YES']

            is_active = parse_bool(row.get('visible', '') or row.get('is_active', ''), True)
            is_featured = parse_bool(row.get('en_vedette', '') or row.get('is_featured', ''), False)
            is_new = parse_bool(row.get('nouveau', '') or row.get('is_new', ''), False)
            short_desc = row.get('description_courte', '') or row.get('short_description', '')

            # Génération auto de SKU si vide
            if not sku:
                cat_prefix = category.slug[:3].upper() if category else 'ONZ'
                sku = f"ONZ-{cat_prefix}-{abs(hash(name)) % 10000:04d}"

            # Recherche si le produit existe déjà par SKU
            product = Product.objects.filter(sku=sku).first()

            if product:
                # Mise à jour
                product.name = name
                product.category = category
                product.brand = brand
                product.price = price
                product.sale_price = sale_price
                product.cost_price = cost_price
                product.stock = stock
                product.min_stock = min_stock
                product.status = status
                product.is_active = is_active
                product.is_featured = is_featured
                product.is_new = is_new
                if short_desc:
                    product.short_description = short_desc
                product.save()
                updated_count += 1
            else:
                # Création
                prod_slug = slugify(name)
                if Product.objects.filter(slug=prod_slug).exists():
                    prod_slug = f"{prod_slug}-{sku.lower()}"

                Product.objects.create(
                    sku=sku,
                    name=name,
                    slug=prod_slug,
                    category=category,
                    brand=brand,
                    price=price,
                    sale_price=sale_price,
                    cost_price=cost_price,
                    stock=stock,
                    min_stock=min_stock,
                    status=status,
                    is_active=is_active,
                    is_featured=is_featured,
                    is_new=is_new,
                    short_description=short_desc,
                    description=short_desc or name,
                )
                created_count += 1

        msg = f"Import terminé avec succès : {created_count} nouveaux produits créés, {updated_count} produits mis à jour."
        if skipped_count:
            msg += f" ({skipped_count} lignes vides ignorées)"
        messages.success(request, msg)

    except Exception as e:
        messages.error(request, f"Erreur lors de l'analyse du fichier CSV : {str(e)}")

    return redirect('backoffice:products')


# ---------------------------------------------------------------------------
# Centre de Contrôle Catalogue & Marketing (Rayons, Marques, Promos, Avis, Fournisseurs)
# ---------------------------------------------------------------------------

@staff_required
def catalog_config_view(request):
    """
    Contrôle centralisé de chaque détail du catalogue et du marketing :
    1. Rayons & Catégories (Nom, parent, ordre, image, actif, suppression)
    2. Marques Officielles (Nom, logo, description, actif, suppression)
    3. Codes Promo & Remises (Code, % ou FCFA, minimum panier, utilisations, actif)
    4. Modération des Avis Clients (Approbation / Masquage / Suppression)
    5. Fournisseurs Magasin (Nom, contact, téléphone, adresse, suppression)
    """
    from orders.models import Coupon
    from shop.models import Review

    active_tab = (request.GET.get('tab') or request.POST.get('tab') or 'categories').strip()

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        def _clear_cat_cache():
            try:
                from django.core.cache import cache
                cache.delete('menu_categories_cached')
            except Exception:
                pass

        try:
            # --- A. RAYONS & CATÉGORIES ---
            if action == 'save_category':
                cat_id = (request.POST.get('category_id') or '').strip()
                name = (request.POST.get('name') or '').strip()
                parent_id = (request.POST.get('parent_id') or '').strip()
                order_val = max(0, int(float(request.POST.get('order') or 0)))
                desc = (request.POST.get('description') or '').strip()
                is_active = request.POST.get('is_active') == 'on'

                if not name:
                    messages.error(request, "Le nom du rayon est obligatoire.")
                else:
                    parent_obj = Category.objects.filter(id=parent_id).first() if parent_id else None
                    if cat_id:
                        cat_obj = get_object_or_404(Category, id=cat_id)
                        if parent_obj and parent_obj.id == cat_obj.id:
                            parent_obj = None
                        cat_obj.name = name
                        cat_obj.parent = parent_obj
                        cat_obj.order = order_val
                        cat_obj.description = desc
                        cat_obj.is_active = is_active
                        if 'image' in request.FILES:
                            cat_obj.image = request.FILES['image']
                        cat_obj.save()
                        messages.success(request, f"Rayon « {cat_obj.name} » mis à jour.")
                    else:
                        base_slug = slugify(name) or 'rayon'
                        slug = base_slug
                        idx = 1
                        while Category.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{idx}"
                            idx += 1
                        cat_obj = Category(
                            name=name,
                            slug=slug,
                            parent=parent_obj,
                            order=order_val,
                            description=desc,
                            is_active=is_active,
                        )
                        if 'image' in request.FILES:
                            cat_obj.image = request.FILES['image']
                        cat_obj.save()
                        messages.success(request, f"Nouveau rayon « {cat_obj.name} » créé.")
                    _clear_cat_cache()
                active_tab = 'categories'

            elif action == 'toggle_category':
                cat_obj = get_object_or_404(Category, id=request.POST.get('category_id'))
                cat_obj.is_active = not cat_obj.is_active
                cat_obj.save(update_fields=['is_active'])
                _clear_cat_cache()
                messages.success(request, f"Statut du rayon « {cat_obj.name} » mis à jour.")
                active_tab = 'categories'

            elif action == 'delete_category':
                cat_obj = get_object_or_404(Category, id=request.POST.get('category_id'))
                p_count = cat_obj.products.count()
                if p_count > 0:
                    messages.error(request, f"Impossible de supprimer « {cat_obj.name} » : {p_count} produit(s) y sont rattachés. Déplacez-les d'abord.")
                else:
                    cname = cat_obj.name
                    cat_obj.delete()
                    _clear_cat_cache()
                    messages.success(request, f"Rayon « {cname} » supprimé.")
                active_tab = 'categories'

            # --- B. MARQUES ---
            elif action == 'save_brand':
                brand_id = (request.POST.get('brand_id') or '').strip()
                name = (request.POST.get('name') or '').strip()
                desc = (request.POST.get('description') or '').strip()
                is_active = request.POST.get('is_active') == 'on'

                if not name:
                    messages.error(request, "Le nom de la marque est obligatoire.")
                else:
                    if brand_id:
                        b_obj = get_object_or_404(Brand, id=brand_id)
                        b_obj.name = name
                        b_obj.description = desc
                        b_obj.is_active = is_active
                        if 'logo' in request.FILES:
                            b_obj.logo = request.FILES['logo']
                        b_obj.save()
                        messages.success(request, f"Marque « {b_obj.name} » mise à jour.")
                    else:
                        base_slug = slugify(name) or 'marque'
                        slug = base_slug
                        idx = 1
                        while Brand.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{idx}"
                            idx += 1
                        b_obj = Brand(
                            name=name,
                            slug=slug,
                            description=desc,
                            is_active=is_active,
                        )
                        if 'logo' in request.FILES:
                            b_obj.logo = request.FILES['logo']
                        b_obj.save()
                        messages.success(request, f"Nouvelle marque « {b_obj.name} » ajoutée.")
                active_tab = 'brands'

            elif action == 'toggle_brand':
                b_obj = get_object_or_404(Brand, id=request.POST.get('brand_id'))
                b_obj.is_active = not b_obj.is_active
                b_obj.save(update_fields=['is_active'])
                messages.success(request, f"Statut de la marque « {b_obj.name} » mis à jour.")
                active_tab = 'brands'

            elif action == 'delete_brand':
                b_obj = get_object_or_404(Brand, id=request.POST.get('brand_id'))
                bname = b_obj.name
                b_obj.delete()
                messages.success(request, f"Marque « {bname} » supprimée.")
                active_tab = 'brands'

            # --- C. CODES PROMO & REMISES ---
            elif action == 'save_coupon':
                coupon_id = (request.POST.get('coupon_id') or '').strip()
                code = (request.POST.get('code') or '').strip().upper().replace(' ', '')
                dtype = request.POST.get('discount_type') or Coupon.DiscountType.PERCENTAGE
                dval = max(1, int(float(request.POST.get('discount_value') or 5)))
                min_amount = max(0, int(float(request.POST.get('min_order_amount') or 0)))
                raw_max = (request.POST.get('max_uses') or '').strip()
                max_uses = max(1, int(float(raw_max))) if raw_max else None
                is_active = request.POST.get('is_active') == 'on'

                if not code:
                    messages.error(request, "Veuillez saisir un code promo (ex: BAMAKO10).")
                else:
                    if coupon_id:
                        cp = get_object_or_404(Coupon, id=coupon_id)
                        cp.code = code
                        cp.discount_type = dtype
                        cp.discount_value = dval
                        cp.min_order_amount = min_amount
                        cp.max_uses = max_uses
                        cp.is_active = is_active
                        cp.save()
                        messages.success(request, f"Code promo « {cp.code} » mis à jour.")
                    else:
                        cp, created = Coupon.objects.update_or_create(
                            code=code,
                            defaults={
                                'discount_type': dtype,
                                'discount_value': dval,
                                'min_order_amount': min_amount,
                                'max_uses': max_uses,
                                'is_active': is_active,
                            }
                        )
                        messages.success(request, f"Code promo « {cp.code} » enregistré.")
                active_tab = 'coupons'

            elif action == 'toggle_coupon':
                cp = get_object_or_404(Coupon, id=request.POST.get('coupon_id'))
                cp.is_active = not cp.is_active
                cp.save(update_fields=['is_active'])
                messages.success(request, f"Code promo « {cp.code} » {'activé' if cp.is_active else 'désactivé'}.")
                active_tab = 'coupons'

            elif action == 'delete_coupon':
                cp = get_object_or_404(Coupon, id=request.POST.get('coupon_id'))
                ccode = cp.code
                cp.delete()
                messages.success(request, f"Code promo « {ccode} » supprimé.")
                active_tab = 'coupons'

            # --- D. AVIS CLIENTS ---
            elif action == 'toggle_review':
                rev = get_object_or_404(Review, id=request.POST.get('review_id'))
                rev.is_approved = not rev.is_approved
                rev.save(update_fields=['is_approved'])
                messages.success(request, f"Avis client {'publié' if rev.is_approved else 'masqué'}.")
                active_tab = 'reviews'

            elif action == 'delete_review':
                rev = get_object_or_404(Review, id=request.POST.get('review_id'))
                rev.delete()
                messages.success(request, "Avis client supprimé.")
                active_tab = 'reviews'

            # --- E. FOURNISSEURS ---
            elif action == 'save_supplier':
                sup_id = (request.POST.get('supplier_id') or '').strip()
                name = (request.POST.get('name') or '').strip()
                contact_name = (request.POST.get('contact_name') or '').strip()
                phone = (request.POST.get('phone') or '').strip()
                email = (request.POST.get('email') or '').strip()
                address = (request.POST.get('address') or '').strip()
                is_active = request.POST.get('is_active') == 'on'

                if not name:
                    messages.error(request, "Le nom du fournisseur est requis.")
                else:
                    if sup_id:
                        sup = get_object_or_404(Supplier, id=sup_id)
                        sup.name = name
                        sup.contact_name = contact_name
                        sup.phone = phone
                        sup.email = email
                        sup.address = address
                        sup.is_active = is_active
                        sup.save()
                        messages.success(request, f"Fournisseur « {sup.name} » mis à jour.")
                    else:
                        sup = Supplier.objects.create(
                            name=name,
                            contact_name=contact_name,
                            phone=phone,
                            email=email,
                            address=address,
                            is_active=is_active,
                        )
                        messages.success(request, f"Fournisseur « {sup.name} » ajouté.")
                active_tab = 'suppliers'

            elif action == 'delete_supplier':
                sup = get_object_or_404(Supplier, id=request.POST.get('supplier_id'))
                sname = sup.name
                sup.delete()
                messages.success(request, f"Fournisseur « {sname} » supprimé.")
                active_tab = 'suppliers'

        except Exception as e:
            messages.error(request, f"Erreur lors de l'opération : {str(e)}")

        return redirect(f"/gestion/catalogue-config/?tab={active_tab}")

    categories = Category.objects.select_related('parent').annotate(prod_count=Count('products')).order_by('order', 'name')
    brands = Brand.objects.annotate(prod_count=Count('products')).order_by('name')
    coupons = Coupon.objects.order_by('-created_at')
    reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:50]
    suppliers = Supplier.objects.order_by('name')

    context = {
        'active_tab': active_tab,
        'categories': categories,
        'brands': brands,
        'coupons': coupons,
        'reviews': reviews,
        'suppliers': suppliers,
        'current_page': 'catalog_config',
    }
    return render(request, 'backoffice/catalog_config.html', context)


# ---------------------------------------------------------------------------
# Centre de Contrôle Emails, Templates, Conditions d'Envoi, Alertes & Rappels
# ---------------------------------------------------------------------------

def _build_sample_order_for_preview():
    """Construit une commande de démonstration réaliste si aucune commande n'existe encore en base."""
    order = Order.objects.prefetch_related('items').order_by('-created_at').first()
    if order:
        return order

    class _DummyItem:
        product_name = "Climatiseur Split Sharp Inverter 1.5 CV (12000 BTU) Gaz R32"
        product_sku = "ONZ-SHPINV-0002"
        quantity = 1
        unit_price = 255000
        total_price = 255000
        def get_total(self):
            return 255000

    class _DummyItemsManager:
        def all(self):
            return [_DummyItem()]

    class _DummyOrder:
        id = 1
        order_number = "ONZ84920175"
        delivery_name = "Moussa Diarra"
        delivery_phone = "+223 76 12 34 56"
        delivery_email = "client@onizukashop.com"
        delivery_city = "Bamako"
        delivery_district = "ACI 2000"
        delivery_address = "Près du Monument de la Paix, Rue 312"
        payment_method = "orange_money"
        payment_reference = "OM261127.1420.A8492"
        subtotal = 255000
        delivery_fee = 0
        discount = 0
        total = 255000
        status = "confirmed"
        created_at = timezone.now()
        items = _DummyItemsManager()
        def get_payment_method_display(self):
            return "Orange Money"
        def get_status_display(self):
            return "Confirmée"
        def get_whatsapp_order_url(self):
            return "https://wa.me/22392673799"

    return _DummyOrder()


@staff_required
def email_template_preview_view(request, template_key):
    """Renvoie le rendu HTML exact d'un des 7 templates d'email pour aperçu visuel en direct (iframe)."""
    from .models import ShopSetting
    shop_settings = ShopSetting.get_settings()
    sample_order = _build_sample_order_for_preview()

    if template_key == 'order_confirmation':
        return render(request, 'emails/order_confirmation.html', {
            'order': sample_order,
            'settings': shop_settings,
            'custom_intro': shop_settings.email_confirmation_intro,
        })
    elif template_key == 'order_status_update':
        return render(request, 'emails/order_status_update.html', {
            'order': sample_order,
            'settings': shop_settings,
            'custom_intro': shop_settings.email_status_intro,
        })
    elif template_key == 'order_payment_reminder':
        return render(request, 'emails/order_payment_reminder.html', {
            'order': sample_order,
            'settings': shop_settings,
            'custom_intro': shop_settings.email_payment_reminder_intro,
        })
    elif template_key == 'abandoned_cart_reminder':
        sample_products = list(Product.objects.filter(is_active=True)[:2])

        class _DummyCartItem:
            def __init__(self, p):
                self.product = p
                self.quantity = 1
            def get_subtotal(self):
                return self.product.current_price

        class _DummyCart:
            def __init__(self, prods):
                self._items = [_DummyCartItem(p) for p in prods]
            def get_items_count(self):
                return len(self._items)
            def get_total(self):
                return sum(i.get_subtotal() for i in self._items)
            def get_whatsapp_cart_url(self):
                return f"https://wa.me/{shop_settings.whatsapp_raw}"

        dummy_cart = _DummyCart(sample_products)
        return render(request, 'emails/abandoned_cart_reminder.html', {
            'cart': dummy_cart,
            'items': dummy_cart._items,
            'client_name': 'Moussa Diarra',
            'settings': shop_settings,
            'promo_code': shop_settings.email_promo_code_reminder or 'BAMAKO5',
            'custom_intro': shop_settings.email_cart_reminder_intro,
        })
    elif template_key == 'admin_new_order_alert':
        return render(request, 'emails/admin_new_order_alert.html', {
            'order': sample_order,
            'settings': shop_settings,
        })
    elif template_key == 'admin_low_stock_alert':
        low_prods = list(Product.objects.filter(is_active=True).order_by('stock')[:4])
        return render(request, 'emails/admin_low_stock_alert.html', {
            'products': low_prods,
            'settings': shop_settings,
        })
    elif template_key == 'admin_contact_message':
        return render(request, 'emails/admin_contact_message.html', {
            'name': 'Amadou Coulibaly',
            'phone': '+223 79 44 55 66',
            'email': 'amadou.coulibaly@bamako.ml',
            'subject': 'Demande de devis 5 Climatiseurs Sharp Inverter 1.5 CV',
            'message': 'Bonjour Onizuka Shop,\nNous souhaitons équiper nos bureaux à ACI 2000 avec 5 climatiseurs Sharp Inverter 1.5 CV et installation complète. Pouvez-vous nous rappeler ?',
            'settings': shop_settings,
        })

    return HttpResponse("Template inconnu", status=404)


@staff_required
def emails_center_view(request):
    """
    Centre de contrôle 100% dédié aux Emails :
    1. Conditions d'envoi & Alertes (Interrupteurs ON/OFF clients & direction + délais de relance)
    2. Templates & Personnalisation (Objets, textes d'introduction, signature, aperçu visuel live + envoi test)
    3. Rappels de Finalisation (Commandes en attente de paiement Orange Money/Wave & Paniers abandonnés, relance 1-clic Email + WhatsApp)
    4. Journal d'envoi des Emails (Historique complet des emails envoyés, ignorés ou échoués)
    """
    from .models import ShopSetting, EmailLog
    from orders.models import Cart
    from orders.emails import (
        send_order_confirmation_email,
        send_order_status_update_email,
        send_order_payment_reminder_email,
        send_abandoned_cart_reminder_email,
        send_admin_order_alert,
        send_low_stock_alert_email,
        send_contact_message_email,
    )

    shop_settings = ShopSetting.get_settings()
    active_tab = (request.GET.get('tab') or request.POST.get('tab') or 'conditions').strip()

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        def _flush_settings_cache():
            try:
                from django.core.cache import cache
                cache.delete('shop_settings_cached')
            except Exception:
                pass

        # --- A. SAUVEGARDE DES CONDITIONS D'ENVOI & ALERTES ---
        if action == 'save_conditions':
            shop_settings.email_notifications_active = request.POST.get('email_notifications_active') == 'on'
            shop_settings.send_order_confirmation_email = request.POST.get('send_order_confirmation_email') == 'on'
            shop_settings.send_order_status_email = request.POST.get('send_order_status_email') == 'on'
            shop_settings.send_payment_reminder_email = request.POST.get('send_payment_reminder_email') == 'on'
            shop_settings.send_cart_abandon_reminder_email = request.POST.get('send_cart_abandon_reminder_email') == 'on'
            shop_settings.send_admin_new_order_alert = request.POST.get('send_admin_new_order_alert') == 'on'
            shop_settings.send_admin_low_stock_alert = request.POST.get('send_admin_low_stock_alert') == 'on'
            shop_settings.send_admin_contact_alert = request.POST.get('send_admin_contact_alert') == 'on'

            shop_settings.email_orders = (request.POST.get('email_orders') or shop_settings.email_orders).strip()
            shop_settings.email_contact = (request.POST.get('email_contact') or shop_settings.email_contact).strip()
            shop_settings.email_sender_name = (request.POST.get('email_sender_name') or 'ONIZUKA SHOP Bamako').strip()
            shop_settings.email_reply_to = (request.POST.get('email_reply_to') or shop_settings.email_contact).strip()

            try:
                shop_settings.payment_reminder_hours = max(1, int(float(request.POST.get('payment_reminder_hours') or 2)))
            except Exception:
                shop_settings.payment_reminder_hours = 2

            try:
                shop_settings.cart_abandon_reminder_hours = max(1, int(float(request.POST.get('cart_abandon_reminder_hours') or 4)))
            except Exception:
                shop_settings.cart_abandon_reminder_hours = 4

            shop_settings.email_promo_code_reminder = (request.POST.get('email_promo_code_reminder') or '').strip().upper()
            shop_settings.save()
            _flush_settings_cache()
            messages.success(request, "Conditions d'envoi, alertes direction et délais de relance enregistrés.")
            return redirect('/gestion/emails/?tab=conditions')

        # --- B. SAUVEGARDE DES TEMPLATES & TEXTES PERSONNALISÉS ---
        elif action == 'save_templates':
            for field_name in (
                'email_confirmation_subject',
                'email_confirmation_intro',
                'email_status_subject',
                'email_status_intro',
                'email_payment_reminder_subject',
                'email_payment_reminder_intro',
                'email_cart_reminder_subject',
                'email_cart_reminder_intro',
                'email_footer_signature',
            ):
                val = (request.POST.get(field_name) or '').strip()
                if val:
                    setattr(shop_settings, field_name, val)
            shop_settings.save()
            _flush_settings_cache()
            messages.success(request, "Les sujets, textes d'introduction et la signature des templates email ont été mis à jour.")
            return redirect('/gestion/emails/?tab=templates')

        # --- C. ENVOI D'UN EMAIL DE TEST ---
        elif action == 'send_test_email':
            test_recipient = (request.POST.get('test_recipient') or shop_settings.email_orders or 'direction@onizukashop.com').strip()
            tpl_type = (request.POST.get('test_template') or 'order_confirmation').strip()
            sample_order = _build_sample_order_for_preview()
            sample_order.delivery_email = test_recipient

            ok = False
            if tpl_type == 'order_confirmation':
                ok = send_order_confirmation_email(sample_order, force=True)
            elif tpl_type == 'order_status_update':
                ok = send_order_status_update_email(sample_order, force=True)
            elif tpl_type == 'order_payment_reminder':
                ok = send_order_payment_reminder_email(sample_order, force=True)
            elif tpl_type == 'admin_new_order_alert':
                ok = send_admin_order_alert(sample_order, force=True)
            elif tpl_type == 'admin_low_stock_alert':
                low_prods = list(Product.objects.filter(is_active=True).order_by('stock')[:3])
                ok = send_low_stock_alert_email(low_prods, force=True)
            elif tpl_type == 'admin_contact_message':
                ok = send_contact_message_email(
                    name="Client Test Bamako",
                    phone="+223 92 67 37 99",
                    email=test_recipient,
                    subject="Test de réception Email Onizuka Shop",
                    message="Ceci est un test officiel envoyé depuis le centre de contrôle /gestion/emails/.",
                    force=True,
                )

            if ok:
                messages.success(request, f"Email de test (« {tpl_type} ») envoyé avec succès à {test_recipient}.")
            else:
                messages.error(request, f"Échec de l'envoi à {test_recipient}. Consultez l'onglet « Journal d'envoi » pour le détail.")
            return redirect(f"/gestion/emails/?tab={active_tab}")

        # --- D. RELANCE 1-CLIC D'UNE COMMANDE EN ATTENTE DE FINALISATION ---
        elif action == 'remind_single_order':
            ord_obj = get_object_or_404(Order, id=request.POST.get('order_id'))
            custom_email = (request.POST.get('delivery_email') or '').strip()
            if custom_email and custom_email != ord_obj.delivery_email:
                ord_obj.delivery_email = custom_email
                ord_obj.save(update_fields=['delivery_email'])

            if send_order_payment_reminder_email(ord_obj, force=True):
                messages.success(request, f"Rappel de finalisation envoyé par email pour la commande #{ord_obj.order_number}.")
            else:
                messages.warning(request, f"Aucun email renseigné pour la commande #{ord_obj.order_number}. Saisissez l'email du client ou relancez-le sur WhatsApp.")
            return redirect('/gestion/emails/?tab=reminders')

        # --- E. RELANCE GROUPÉE DE TOUTES LES COMMANDES EN ATTENTE ---
        elif action == 'remind_all_pending_orders':
            pending_qs = Order.objects.filter(
                status=Order.Status.PENDING,
                payment_status=False,
            )
            sent_cnt = 0
            for ord_obj in pending_qs:
                if (ord_obj.delivery_email or (ord_obj.user and ord_obj.user.email)):
                    if send_order_payment_reminder_email(ord_obj, force=True):
                        sent_cnt += 1
            messages.success(request, f"{sent_cnt} email(s) de rappel de finalisation envoyé(s) aux commandes en attente.")
            return redirect('/gestion/emails/?tab=reminders')

        # --- F. RELANCE 1-CLIC D'UN PANIER ABANDONNÉ ---
        elif action == 'remind_single_cart':
            cart_obj = get_object_or_404(Cart, id=request.POST.get('cart_id'))
            custom_email = (request.POST.get('guest_email') or '').strip()
            if custom_email and custom_email != cart_obj.guest_email:
                cart_obj.guest_email = custom_email
                cart_obj.save(update_fields=['guest_email'])

            if send_abandoned_cart_reminder_email(cart_obj, force=True):
                messages.success(request, f"Rappel de panier abandonné envoyé à {cart_obj.guest_email or cart_obj.user.email}.")
            else:
                messages.warning(request, "Veuillez renseigner une adresse email pour ce panier ou utiliser le bouton WhatsApp.")
            return redirect('/gestion/emails/?tab=reminders')

        # --- G. ALERTE STOCK BAS MANUELLE IMMÉDIATE ---
        elif action == 'send_low_stock_digest_now':
            low_prods = list(
                Product.objects.filter(is_active=True, track_stock=True, stock__lte=models.F('min_stock')).order_by('stock')
            )
            if not low_prods:
                low_prods = list(Product.objects.filter(is_active=True).order_by('stock')[:5])
            if send_low_stock_alert_email(low_prods, force=True):
                messages.success(request, f"Rapport d'alerte stock ({len(low_prods)} articles) envoyé à {shop_settings.email_orders}.")
            else:
                messages.error(request, "Erreur lors de l'envoi de l'alerte stock.")
            return redirect('/gestion/emails/?tab=conditions')

        # --- H. PURGER LE JOURNAL DES EMAILS ---
        elif action == 'clear_email_logs':
            EmailLog.objects.all().delete()
            messages.success(request, "Le journal des envois d'emails a été vidé.")
            return redirect('/gestion/emails/?tab=logs')

    # Données pour l'onglet Rappels de Finalisation
    pending_orders = (
        Order.objects
        .select_related('user')
        .prefetch_related('items')
        .filter(status__in=[Order.Status.PENDING, Order.Status.CONFIRMED], payment_status=False)
        .order_by('-created_at')[:30]
    )

    abandoned_carts = (
        Cart.objects
        .select_related('user')
        .prefetch_related('items__product')
        .annotate(items_cnt=Count('items'))
        .filter(items_cnt__gt=0)
        .order_by('-updated_at')[:30]
    )

    email_logs = EmailLog.objects.all()[:60]
    logs_sent_count = EmailLog.objects.filter(status=EmailLog.Status.SENT).count()
    logs_failed_count = EmailLog.objects.filter(status=EmailLog.Status.FAILED).count()

    template_cards = [
        {
            'key': 'order_confirmation',
            'title': '1. Confirmation de Commande (Client)',
            'badge': 'Automatique à l\'achat',
            'desc': 'Facture récapitulative complète avec articles, total FCFA et instructions Orange Money / Wave / Livraison.',
        },
        {
            'key': 'order_payment_reminder',
            'title': '2. Rappel de Finalisation / Paiement (Client)',
            'badge': 'Relance Commande',
            'desc': 'Rappelle au client que ses appareils sont réservés à Dibidani avec bouton 1-clic pour finaliser par Orange Money, Wave ou WhatsApp.',
        },
        {
            'key': 'abandoned_cart_reminder',
            'title': '3. Rappel de Panier Abandonné (Client)',
            'badge': 'Relance Panier',
            'desc': 'Relance les visiteurs ayant laissé des appareils dans leur panier (avec code promo optionnel et lien WhatsApp).',
        },
        {
            'key': 'order_status_update',
            'title': '4. Mise à Jour du Statut de Livraison (Client)',
            'badge': 'Suivi temps réel',
            'desc': 'Envoyé dès que vous cliquez sur « Confirmer », « En livraison », « Livrée » ou « Annuler » dans la gestion.',
        },
        {
            'key': 'admin_new_order_alert',
            'title': '5. Alerte Nouvelle Commande (Direction)',
            'badge': 'Alerte Interne',
            'desc': 'Envoyé immédiatement à la Direction avec coordonnées du client, quartier à Bamako, téléphone et lien direct ERP.',
        },
        {
            'key': 'admin_low_stock_alert',
            'title': '6. Alerte Stock Bas / Rupture (Direction)',
            'badge': 'Alerte Stock',
            'desc': 'Envoyé automatiquement lorsqu\'un produit passe sous son seuil de stock minimum après une commande.',
        },
        {
            'key': 'admin_contact_message',
            'title': '7. Alerte Message Formulaire Contact (Direction)',
            'badge': 'Service Client',
            'desc': 'Transmet tout message ou demande de devis envoyé depuis la page Contact avec bouton « Répondre sur WhatsApp ».',
        },
    ]

    context = {
        'settings': shop_settings,
        'active_tab': active_tab,
        'pending_orders': pending_orders,
        'abandoned_carts': abandoned_carts,
        'email_logs': email_logs,
        'logs_sent_count': logs_sent_count,
        'logs_failed_count': logs_failed_count,
        'template_cards': template_cards,
        'current_page': 'emails',
    }
    return render(request, 'backoffice/emails_center.html', context)



