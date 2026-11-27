"""
ONIZOUKA SHOP - Views du shop
homepage, catalog, product_detail, search, category
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Min, Max
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_htmx.http import trigger_client_event

from shop.models import Product, Category, Brand, Review
from orders.models import Cart, CartItem

import django_filters


# ---------------------------------------------------------------------------
# Filtres
# ---------------------------------------------------------------------------

class ProductFilter(django_filters.FilterSet):
    prix_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Prix min')
    prix_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Prix max')
    marque = django_filters.ModelMultipleChoiceFilter(
        field_name='brand',
        queryset=Brand.objects.filter(is_active=True),
        label='Marque',
    )
    en_promo = django_filters.BooleanFilter(
        field_name='sale_price', lookup_expr='isnull', exclude=True, label='En promo'
    )
    en_stock = django_filters.BooleanFilter(method='filter_stock', label='En stock')
    tri = django_filters.OrderingFilter(
        fields=(
            ('price', 'prix_asc'),
            ('-price', 'prix_desc'),
            ('-created_at', 'nouveautes'),
            ('name', 'nom'),
        ),
        field_name='tri',
        label='Trier par',
    )

    class Meta:
        model = Product
        fields = ['prix_min', 'prix_max', 'marque', 'en_promo']

    def filter_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create_cart(request):
    """Recupere ou cree le panier pour l'utilisateur / la session de maniere ultra-robuste et atomique."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Fusionner panier session (via cart_id stocke en session ou session_key)
        session_cart_id = request.session.get('cart_id') if hasattr(request, 'session') else None
        session_carts = []

        if session_cart_id:
            c = Cart.objects.filter(id=session_cart_id).exclude(id=cart.id).first()
            if c and c not in session_carts:
                session_carts.append(c)

        if hasattr(request, 'session') and request.session.session_key:
            for sc in Cart.objects.filter(session_key=request.session.session_key).exclude(id=cart.id):
                if sc not in session_carts:
                    session_carts.append(sc)

        for sc in session_carts:
            for item in sc.items.select_related('product').all():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart, product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save(update_fields=['quantity'])
            sc.delete()

        if hasattr(request, 'session'):
            request.session['cart_id'] = cart.id
        return cart

    # Utilisateur anonyme
    session_key = None
    if hasattr(request, 'session'):
        if not request.session.session_key:
            try:
                request.session.save()
            except Exception:
                pass
        session_key = request.session.session_key

    # Verifier si un cart_id valide existe deja en session
    cart = None
    if hasattr(request, 'session'):
        session_cart_id = request.session.get('cart_id')
        if session_cart_id:
            cart = Cart.objects.filter(id=session_cart_id, user__isnull=True).first()

    if not cart and session_key:
        cart = Cart.objects.filter(session_key=session_key).first()

    if not cart:
        if not session_key:
            import uuid
            session_key = uuid.uuid4().hex[:32]
        try:
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        except Exception:
            cart = Cart.objects.filter(session_key=session_key).first()
            if not cart:
                import uuid
                cart = Cart.objects.create(session_key=uuid.uuid4().hex[:32])

    if hasattr(request, 'session'):
        request.session['cart_id'] = cart.id

    return cart




# ---------------------------------------------------------------------------
# Homepage (Architecture Marketplace Mobile-First & Flux Dynamique HTMX)
# ---------------------------------------------------------------------------

def home(request):
    in_stock_q = Q(is_active=True, status='active') & (Q(track_stock=False) | Q(stock__gt=0))

    # Filtrage dynamique du flux "Découverte" (onglets HTMX + bouton Voir plus)
    active_tab = request.GET.get('tab', 'tous').strip()
    feed_qs = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images')

    if active_tab == 'promos':
        feed_qs = feed_qs.filter(sale_price__isnull=False).order_by('-is_featured', '-created_at')
    elif active_tab == 'nouveautes':
        feed_qs = feed_qs.order_by('-created_at')
    elif active_tab and active_tab != 'tous':
        cat_obj = Category.objects.filter(slug=active_tab, is_active=True).first()
        if cat_obj:
            descendants = cat_obj.get_descendants(include_self=True)
            feed_qs = feed_qs.filter(category__in=descendants).order_by('-is_featured', '-created_at')
        else:
            feed_qs = feed_qs.order_by('-is_featured', '-created_at')
    else:
        feed_qs = feed_qs.order_by('-is_featured', '-created_at')

    feed_paginator = Paginator(feed_qs, 20)
    feed_page = feed_paginator.get_page(request.GET.get('page', 1))

    # Requête partielle HTMX (changement d'onglet ou bouton "Voir plus")
    if request.htmx or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        append_mode = request.GET.get('append') == '1'
        return render(request, 'shop/partials/home_feed.html', {
            'feed_products': feed_page,
            'active_tab': active_tab,
            'append_mode': append_mode,
        })

    # Produits phares pour le Slider Hero compact (sélection diversifiée : 1 produit par marque majeure)
    hero_candidates = list(Product.objects.filter(
        in_stock_q, price__gt=0, images__isnull=False
    ).select_related('brand', 'category').prefetch_related('images').distinct().order_by('-is_featured', '-created_at')[:30])
    hero_products = []
    seen_brands = set()
    for hp in hero_candidates:
        b_key = hp.brand_id or hp.name[:10]
        if b_key not in seen_brands:
            seen_brands.add(b_key)
            hero_products.append(hp)
        if len(hero_products) >= 5:
            break
    if len(hero_products) < 5:
        for hp in hero_candidates:
            if hp not in hero_products:
                hero_products.append(hp)
            if len(hero_products) >= 5:
                break

    # Offres Flash / SuperDeals (produits remisés, complétés par les vedettes si besoin)
    sale_products = list(Product.objects.filter(
        in_stock_q, sale_price__isnull=False
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')[:10])

    featured_products = list(Product.objects.filter(
        in_stock_q, is_featured=True
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')[:8])

    new_products = list(Product.objects.filter(
        in_stock_q
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')[:6])

    def fill_up_to(items, target):
        if len(items) >= target:
            return items[:target]
        seen = {p.id for p in items}
        extras = list(Product.objects.filter(in_stock_q).exclude(id__in=seen).select_related('brand', 'category').prefetch_related('images')[:target - len(items)])
        return (items + extras)[:target]

    sale_products = fill_up_to(sale_products, 8)
    featured_products = fill_up_to(featured_products, 6)
    new_products = fill_up_to(new_products, 6)

    # Catégories racines avec miniature produit 100% dynamique (zéro chemin codé en dur)
    root_categories = list(Category.objects.filter(
        parent__isnull=True, is_active=True
    ).order_by('order', 'name')[:10])

    # Associer une image représentative et le compteur à chaque catégorie en 1 passe légère
    cat_ids = [c.id for c in root_categories]
    sample_products = list(Product.objects.filter(
        is_active=True, category_id__in=cat_ids, images__isnull=False
    ).prefetch_related('images').order_by('-is_featured', '-created_at'))
    cat_thumb_map = {}
    for sp in sample_products:
        if sp.category_id not in cat_thumb_map and sp.primary_image:
            try:
                cat_thumb_map[sp.category_id] = sp.primary_image.thumbnail.url
            except Exception:
                cat_thumb_map[sp.category_id] = sp.primary_image.image.url

    for cat in root_categories:
        if cat.image:
            cat.thumb_url = cat.image.url
        else:
            cat.thumb_url = cat_thumb_map.get(cat.id, '')

    brands = list(Brand.objects.filter(is_active=True, products__is_active=True).distinct().order_by('name')[:16])
    total_active_products = Product.objects.filter(is_active=True).count()

    # Produits avec démonstration vidéo
    video_products = list(
        Product.objects.filter(is_active=True)
        .filter(Q(video_file__isnull=False) & ~Q(video_file='') | ~Q(video_url=''))
        .select_related('brand', 'category')
        .prefetch_related('images')
        .order_by('-is_featured', '-created_at')[:8]
    )

    # Produits vus récemment (session)
    recent_ids = [int(pid) for pid in (request.session.get('recently_viewed') or []) if str(pid).isdigit()][:8]
    recently_viewed_products = []
    if recent_ids:
        rv_map = {
            p.id: p for p in Product.objects.filter(id__in=recent_ids, is_active=True)
            .select_related('brand', 'category').prefetch_related('images')
        }
        recently_viewed_products = [rv_map[i] for i in recent_ids if i in rv_map]

    context = {
        'hero_products': hero_products,
        'featured_products': featured_products,
        'new_products': new_products,
        'sale_products': sale_products,
        'video_products': video_products,
        'recently_viewed_products': recently_viewed_products,
        'feed_products': feed_page,
        'active_tab': active_tab,
        'root_categories': root_categories,
        'brands': brands,
        'total_active_products': total_active_products,
        'page_title': 'Onizouka Shop • Électroménager, Meubles, Déco & Maison à Bamako',
        'meta_description': "Onizouka Shop au Grand Marché de Bamako : Électroménager, Meubles, Décoration, Climatiseurs, Frigos et Smart TV au meilleur prix en FCFA. Vidéos réelles et livraison 24h.",
    }
    return render(request, 'shop/home.html', context)


# ---------------------------------------------------------------------------
# Helpers Filtres Intelligents Multi-Rayons (Électro, Meubles, Déco, etc.)
# ---------------------------------------------------------------------------

BUDGET_BRACKETS = [
    ('lt100k', 'Moins de 100 000 F', None, 100000),
    ('100k_300k', '100k – 300k F', 100000, 300000),
    ('300k_600k', '300k – 600k F', 300000, 600000),
    ('gt600k', '600 000 F et +', 600000, None),
]


def _get_smart_chips_for_category(category, base_qs):
    """Génère dynamiquement des puces de filtrage pertinentes selon l'univers (Meubles, Déco, Clim, Frigo, TV, etc.)."""
    presets = []
    cat_key = f"{category.slug} {category.name}".lower() if category else ''
    if any(k in cat_key for k in ('clim', 'split')):
        presets = ['1 CV', '1.5 CV', '2 CV', '3 CV', 'Inverter', '9000 BTU', '12000 BTU', '18000 BTU']
    elif any(k in cat_key for k in ('frigo', 'refrig', 'congel')):
        presets = ['No Frost', 'Combiné', '2 Portes', 'Américain', 'Inverter', 'Vitrine']
    elif any(k in cat_key for k in ('tele', 'tv', 'image')):
        presets = ['32"', '43"', '50"', '55"', '65"', '4K', 'Smart TV', 'QLED']
    elif any(k in cat_key for k in ('meuble', 'mobilier', 'salon', 'literie')):
        presets = ['Salon', 'Canapé', 'Lit', 'Armoire', 'Table', 'Bureau', 'Bois', 'Cuir', 'Velours']
    elif any(k in cat_key for k in ('deco', 'luminaire', 'lustre', 'tapis')):
        presets = ['Lustre', 'LED', 'Tapis', 'Tableau', 'Miroir', 'Rideau', 'Doré', 'Moderne']
    elif any(k in cat_key for k in ('cuisin', 'four', 'petit')):
        presets = ['4 Feux', '5 Feux', 'Inox', 'Four', 'Mixeur', 'Micro-ondes']
    else:
        presets = ['Inverter', 'No Frost', '4K', 'Salon', 'Lustre', 'Inox']

    # Compléter automatiquement avec des valeurs courtes présentes dans specifications JSON
    spec_vals = []
    for specs in base_qs.exclude(specifications={}).values_list('specifications', flat=True)[:40]:
        if isinstance(specs, dict):
            for v in specs.values():
                sv = str(v).strip()
                if 2 <= len(sv) <= 18 and sv not in presets and sv not in spec_vals:
                    spec_vals.append(sv)
                    if len(spec_vals) >= 6:
                        break
        if len(spec_vals) >= 6:
            break

    # Garder uniquement les puces qui retournent au moins 1 produit dans le rayon courant (ou garder les presets utiles)
    active_chips = []
    for chip in (presets + spec_vals):
        if len(active_chips) >= 10:
            break
        exists = base_qs.filter(
            Q(name__icontains=chip) |
            Q(short_description__icontains=chip) |
            Q(description__icontains=chip) |
            Q(specifications__icontains=chip)
        ).exists()
        if exists and chip not in active_chips:
            active_chips.append(chip)
    return active_chips


def _apply_smart_catalog_filters(request, qs):
    """Applique les filtres rapides (budget 1-clic, vidéo, éco/solaire, mot-clé technique/matière)."""
    budget = (request.GET.get('budget') or '').strip()
    for code, _lbl, bmin, bmax in BUDGET_BRACKETS:
        if budget == code:
            if bmin is not None:
                qs = qs.filter(price__gte=bmin)
            if bmax is not None:
                qs = qs.filter(price__lte=bmax)
            break

    if request.GET.get('avec_video') == 'true':
        qs = qs.filter(Q(video_file__isnull=False) & ~Q(video_file='') | ~Q(video_url=''))

    if request.GET.get('eco_solaire') == 'true':
        qs = qs.filter(is_eco_solar=True)

    tag = (request.GET.get('tag') or '').strip()
    if tag:
        qs = qs.filter(
            Q(name__icontains=tag) |
            Q(short_description__icontains=tag) |
            Q(description__icontains=tag) |
            Q(specifications__icontains=tag)
        )
    return qs


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------

def catalog(request):
    """Catalogue general multi-univers avec filtres intelligents et pagination"""
    products_qs = Product.objects.filter(
        is_active=True
    ).select_related('brand', 'category').prefetch_related('images').order_by('-created_at')

    smart_chips = _get_smart_chips_for_category(None, products_qs)
    f = ProductFilter(request.GET, queryset=products_qs)
    products_filtered = _apply_smart_catalog_filters(request, f.qs)

    sort = request.GET.get('tri', 'nouveautes')
    sort_map = {
        'prix_asc': 'price',
        'prix_desc': '-price',
        'nouveautes': '-created_at',
        'nom': 'name',
        'promo': '-sale_price',
    }
    products_filtered = products_filtered.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products_filtered, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    price_range = products_qs.aggregate(min_p=Min('price'), max_p=Max('price'))
    brands = Brand.objects.filter(is_active=True, products__is_active=True).distinct()
    all_categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order', 'name')

    context = {
        'products': page_obj,
        'filter': f,
        'brands': brands,
        'all_categories': all_categories,
        'smart_chips': smart_chips,
        'budget_brackets': BUDGET_BRACKETS,
        'selected_budget': request.GET.get('budget', ''),
        'selected_tag': request.GET.get('tag', ''),
        'selected_brands': request.GET.getlist('marque'),
        'price_min': price_range['min_p'] or 0,
        'price_max': price_range['max_p'] or 10000000,
        'total_count': products_filtered.count(),
        'sort': sort,
        'append_mode': request.GET.get('append') == '1',
        'page_title': 'Boutique Complète • Électroménager, Meubles & Déco - Onizouka Shop',
        'meta_description': 'Parcourez tous nos rayons : électroménager, meubles, salons, décoration et électronique à Bamako.',
    }

    if request.htmx:
        if request.GET.get('append') == '1':
            return render(request, 'shop/partials/product_grid.html', context)
        return render(request, 'shop/partials/catalog_workspace.html', context)
    return render(request, 'shop/catalog.html', context)


# ---------------------------------------------------------------------------
# Categorie
# ---------------------------------------------------------------------------

def category_detail(request, slug):
    """Produits d'une categorie (et sous-categories) avec filtres métier dynamiques"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    descendants = category.get_descendants(include_self=True)

    products_qs = Product.objects.filter(
        is_active=True, category__in=descendants
    ).select_related('brand', 'category').prefetch_related('images')

    smart_chips = _get_smart_chips_for_category(category, products_qs)
    f = ProductFilter(request.GET, queryset=products_qs)
    products_filtered = _apply_smart_catalog_filters(request, f.qs)

    sort = request.GET.get('tri', 'nouveautes')
    sort_map = {
        'prix_asc': 'price',
        'prix_desc': '-price',
        'nouveautes': '-created_at',
        'nom': 'name',
    }
    products_filtered = products_filtered.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products_filtered, 24)
    page_obj = paginator.get_page(request.GET.get('page'))

    price_range = products_qs.aggregate(min_p=Min('price'), max_p=Max('price'))
    brands = Brand.objects.filter(
        is_active=True, products__is_active=True, products__category__in=descendants
    ).distinct()
    all_categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order', 'name')

    context = {
        'category': category,
        'products': page_obj,
        'filter': f,
        'brands': brands,
        'all_categories': all_categories,
        'smart_chips': smart_chips,
        'budget_brackets': BUDGET_BRACKETS,
        'selected_budget': request.GET.get('budget', ''),
        'selected_tag': request.GET.get('tag', ''),
        'selected_brands': request.GET.getlist('marque'),
        'price_min': price_range['min_p'] or 0,
        'price_max': price_range['max_p'] or 10000000,
        'total_count': products_filtered.count(),
        'sort': sort,
        'append_mode': request.GET.get('append') == '1',
        'breadcrumbs': list(category.get_ancestors(include_self=True)),
        'page_title': f'{category.name} - Onizouka Shop Bamako',
        'meta_description': category.meta_description or f'Découvrez notre rayon {category.name} au Grand Marché de Bamako.',
    }

    if request.htmx:
        if request.GET.get('append') == '1':
            return render(request, 'shop/partials/product_grid.html', context)
        return render(request, 'shop/partials/catalog_workspace.html', context)
    return render(request, 'shop/catalog.html', context)


# ---------------------------------------------------------------------------
# Fiche produit
# ---------------------------------------------------------------------------

def product_detail(request, slug):
    """Fiche produit complete"""
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('images', 'reviews__user'),
        slug=slug, is_active=True
    )

    reviews = product.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    avg_rating = product.get_average_rating()

    # Produits similaires (grille dense Marketplace)
    related_products = list(Product.objects.filter(
        is_active=True, category=product.category
    ).exclude(pk=product.pk).select_related('brand', 'category').prefetch_related('images')[:10])
    if len(related_products) < 6:
        seen_ids = [product.pk] + [rp.pk for rp in related_products]
        extra_related = list(Product.objects.filter(
            is_active=True
        ).exclude(pk__in=seen_ids).select_related('brand', 'category').prefetch_related('images')[:10 - len(related_products)])
        related_products.extend(extra_related)

    # L'utilisateur a-t-il deja un avis ?
    user_review = None
    can_review = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        # Verifier si l'utilisateur a achete le produit
        from orders.models import OrderItem
        has_bought = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'
        ).exists()
        can_review = has_bought and not user_review

    # Mémoriser et charger les produits "Vu récemment" (hors produit courant)
    rv_list = [int(pid) for pid in (request.session.get('recently_viewed') or []) if str(pid).isdigit()]
    other_rv_ids = [pid for pid in rv_list if pid != product.pk][:6]
    recently_viewed_products = []
    if other_rv_ids:
        rv_map = {
            p.id: p for p in Product.objects.filter(id__in=other_rv_ids, is_active=True)
            .select_related('brand', 'category').prefetch_related('images')
        }
        recently_viewed_products = [rv_map[i] for i in other_rv_ids if i in rv_map]

    new_rv = [product.pk] + [pid for pid in rv_list if pid != product.pk]
    request.session['recently_viewed'] = new_rv[:10]

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
        'recently_viewed_products': recently_viewed_products,
        'user_review': user_review,
        'can_review': can_review,
        'stars_range': range(1, 6),
        'breadcrumbs': list(product.category.get_ancestors(include_self=True)),
        'page_title': product.meta_title or f'{product.name} - Onizouka Shop',
        'meta_description': product.meta_description or product.short_description,
    }
    return render(request, 'shop/product_detail.html', context)


# ---------------------------------------------------------------------------
# Recherche & Autocomplétion Live Instantanée (HTMX)
# ---------------------------------------------------------------------------

def _build_accent_tolerant_q(query):
    """Recherche tolérante aux accents (ex: refrigerateur <-> réfrigérateur, meuble, deco <-> déco)."""
    import unicodedata
    stripped = ''.join(
        c for c in unicodedata.normalize('NFD', query) if unicodedata.category(c) != 'Mn'
    )
    variants = {query}
    if stripped and stripped.lower() != query.lower():
        variants.add(stripped)
    # Ajouter quelques équivalences françaises fréquentes
    for base_w, acc_w in [('refrigerateur', 'réfrigérateur'), ('congelateur', 'congélateur'), ('televiseur', 'téléviseur'), ('decoration', 'décoration'), ('cuisiniere', 'cuisinière'), ('canape', 'canapé')]:
        if base_w in stripped.lower():
            variants.add(stripped.lower().replace(base_w, acc_w))
    q_obj = Q()
    for v in variants:
        q_obj |= (
            Q(name__icontains=v) |
            Q(short_description__icontains=v) |
            Q(description__icontains=v) |
            Q(brand__name__icontains=v) |
            Q(category__name__icontains=v) |
            Q(sku__icontains=v)
        )
    return q_obj


def live_search(request):
    """Résultats instantanés HTMX sous la barre de recherche dès 2 caractères."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return render(request, 'shop/partials/live_search_results.html', {'query': query, 'results': [], 'categories': []})

    q_filter = _build_accent_tolerant_q(query)
    results = list(
        Product.objects.filter(q_filter, is_active=True)
        .select_related('brand', 'category')
        .prefetch_related('images')
        .distinct()
        .order_by('-is_featured', '-created_at')[:6]
    )
    categories = list(
        Category.objects.filter(Q(name__icontains=query) | Q(slug__icontains=query), is_active=True)[:3]
    )
    return render(request, 'shop/partials/live_search_results.html', {
        'query': query,
        'results': results,
        'categories': categories,
    })


def search(request):
    """Recherche fulltext tolérante aux accents dans tous les rayons avec tri/filtres live"""
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('tri', 'pertinence')
    products_qs = Product.objects.none()
    total = 0

    if query:
        q_filter = _build_accent_tolerant_q(query)
        products_qs = Product.objects.filter(
            q_filter,
            is_active=True
        ).select_related('brand', 'category').prefetch_related('images').distinct()
        products_qs = _apply_smart_catalog_filters(request, products_qs)
        if sort == 'prix_asc':
            products_qs = products_qs.order_by('price')
        elif sort == 'prix_desc':
            products_qs = products_qs.order_by('-price')
        else:
            products_qs = products_qs.order_by('-is_featured', '-created_at')

        total = products_qs.count()
        paginator = Paginator(products_qs, 24)
        products = paginator.get_page(request.GET.get('page'))
    else:
        products = Product.objects.none()

    context = {
        'query': query,
        'sort': sort,
        'products': products,
        'total': total,
        'append_mode': request.GET.get('append') == '1',
        'page_title': f'Recherche : {query} - Onizouka Shop' if query else 'Recherche - Onizouka Shop',
    }

    if request.htmx and request.GET.get('append') == '1':
        return render(request, 'shop/partials/product_grid.html', context)
    return render(request, 'shop/search.html', context)


# ---------------------------------------------------------------------------
# Contact & Boutique Bamako
# ---------------------------------------------------------------------------

def contact(request):
    """Page de contact officielle et Boutique Bamako"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and phone and message:
            try:
                from orders.emails import send_contact_message_email
                send_contact_message_email(name, phone, email, subject, message)
            except Exception:
                pass

            messages.success(
                request,
                f"Merci {name} ! Votre message a bien été reçu par notre équipe de Bamako. Un conseiller vous contactera rapidement par appel ou WhatsApp."
            )
            return redirect('shop:contact')
        else:
            messages.error(request, "Veuillez renseigner au minimum votre nom, votre numéro de téléphone et votre message.")

    context = {
        'page_title': 'Contact & Boutique Grand Marché - Onizouka Shop',
        'meta_description': 'Contactez notre boutique au Grand Marché de Bamako. Service client WhatsApp 7j/7, devis et assistance après-vente garantie.',
    }
    return render(request, 'shop/contact.html', context)


def terms_view(request):
    """Conditions Générales de Vente (CGV)."""
    return render(request, 'shop/cgv.html', {'page_title': 'Conditions Générales de Vente - Onizouka Shop'})


def privacy_view(request):
    """Politique de Confidentialité et Protection des Données."""
    return render(request, 'shop/privacy.html', {'page_title': 'Politique de Confidentialité - Onizouka Shop'})


def legal_view(request):
    """Mentions Légales de la Société."""
    return render(request, 'shop/legal.html', {'page_title': 'Mentions Légales - Onizouka Shop'})


def shipping_warranty_view(request):
    """Politique de Livraison à Bamako, Retrait Magasin & Garantie Constructeur."""
    return render(request, 'shop/shipping_warranty.html', {'page_title': 'Livraison & Garantie - Onizouka Shop'})


@login_required
@require_POST
def add_review(request, slug):
    """Soumettre un avis client sur un produit"""
    from .models import Review
    product = get_object_or_404(Product, slug=slug, is_active=True)

    try:
        rating = int(request.POST.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    title = request.POST.get('title', '').strip()
    body = request.POST.get('body', '').strip()

    if not body:
        messages.error(request, 'Veuillez saisir votre commentaire pour publier votre avis.')
        return redirect(f"{product.get_absolute_url()}#avis")

    from orders.models import OrderItem
    has_bought = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
    ).exists()

    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating,
            'title': title or f"Avis de {request.user.first_name or request.user.username}",
            'body': body,
            'is_verified': has_bought,
            'is_approved': True,
        }
    )

    action_word = "enregistré" if created else "mis à jour"
    messages.success(request, f"Votre avis a été {action_word} avec succès. Merci pour votre retour !")
    return redirect(f"{product.get_absolute_url()}#avis")


def wishlist_toggle(request, product_id):
    """Ajouter ou retirer un produit des favoris du client sans rechargement de page"""
    from .models import Wishlist
    from django.urls import reverse

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json' or request.method == 'POST'

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'login_required': True,
                'login_url': reverse('account_login') + f'?next={request.META.get("HTTP_REFERER", "/")}',
                'message': 'Connectez-vous pour enregistrer vos favoris.'
            })
        messages.info(request, "Veuillez vous connecter pour enregistrer vos favoris.")
        return redirect('account_login')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    fav = Wishlist.objects.filter(user=request.user, product=product).first()

    if fav:
        fav.delete()
        is_favorited = False
        msg = f"« {product.name} » a été retiré de vos favoris."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        is_favorited = True
        msg = f"« {product.name} » a été ajouté à vos favoris !"

    total_favs = Wishlist.objects.filter(user=request.user).count()

    if is_ajax:
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'count': total_favs,
            'message': msg
        })

    messages.info(request, msg)
    next_url = request.META.get('HTTP_REFERER') or 'shop:wishlist'
    return redirect(next_url)


@login_required
def wishlist_view(request):
    """Afficher la liste des produits favoris du client"""
    from .models import Wishlist
    wishlist_items = (
        Wishlist.objects
        .filter(user=request.user)
        .select_related('product__brand', 'product__category')
        .prefetch_related('product__images')
        .order_by('-created_at')
    )
    products = [item.product for item in wishlist_items if item.product.is_active]

    context = {
        'products': products,
        'total_count': len(products),
        'page_title': 'Mes Favoris - Onizouka Shop',
    }
    return render(request, 'shop/wishlist.html', context)


def facebook_catalog_feed(request):
    """Génère le flux XML officiel du catalogue produits pour Meta Commerce Manager (Facebook, Instagram & WhatsApp Catalog)."""
    products = (
        Product.objects
        .filter(is_active=True, price__gt=0)
        .select_related('brand', 'category')
        .prefetch_related('images')
        .order_by('-is_featured', '-created_at')
    )
    base_url = f"{request.scheme}://{request.get_host()}"
    return render(
        request, 
        'shop/facebook_catalog.xml', 
        {'products': products, 'base_url': base_url}, 
        content_type='application/xml; charset=utf-8'
    )


def pwa_offline_view(request):
    """Page de secours hors-ligne pour la PWA et l'application mobile Capacitor."""
    return render(request, 'shop/offline.html')


def pwa_manifest(request):
    """Manifest Web App officiel (PWA Pro & Capacitor Ready - Android, iOS & Desktop)."""
    from backoffice.models import ShopSetting
    cfg = ShopSetting.get_settings()
    site_name = cfg.site_name or "ONIZUKA SHOP"
    manifest = {
        "id": "/?source=pwa",
        "name": f"{site_name} • Électroménager & Climatisation Bamako",
        "short_name": "Onizuka Shop",
        "description": "Application officielle Onizuka Shop au Grand Marché de Bamako (Dibidani). Climatiseurs, Ventilateurs Solaires, Réfrigérateurs, Smart TV et commande rapide WhatsApp.",
        "start_url": "/?source=pwa",
        "scope": "/",
        "display": "standalone",
        "display_override": ["window-controls-overlay", "standalone", "minimal-ui"],
        "orientation": "portrait-primary",
        "background_color": "#0d0e12",
        "theme_color": "#0d0e12",
        "lang": "fr",
        "dir": "ltr",
        "prefer_related_applications": False,
        "categories": ["shopping", "lifestyle", "business"],
        "launch_handler": {
            "client_mode": ["navigate-existing", "auto"]
        },
        "icons": [
            {
                "src": "/static/images/pwa/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any"
            },
            {
                "src": "/static/images/pwa/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any"
            },
            {
                "src": "/static/images/pwa/icon-maskable-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable"
            },
            {
                "src": "/static/images/app-icon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any"
            }
        ],
        "shortcuts": [
            {
                "name": "Catalogue Climatiseurs & Électro",
                "short_name": "Catalogue",
                "description": "Parcourir tous les appareils en stock à Bamako",
                "url": "/catalogue/?source=pwa_shortcut",
                "icons": [{"src": "/static/images/pwa/icon-192.png", "sizes": "192x192", "type": "image/png"}]
            },
            {
                "name": "Mon Panier",
                "short_name": "Panier",
                "description": "Valider ma commande ou envoyer sur WhatsApp",
                "url": "/panier/?source=pwa_shortcut",
                "icons": [{"src": "/static/images/pwa/icon-192.png", "sizes": "192x192", "type": "image/png"}]
            },
            {
                "name": "Suivre ma Commande",
                "short_name": "Suivi ONZ",
                "description": "Suivi en direct par numéro de commande",
                "url": "/panier/suivi/?source=pwa_shortcut",
                "icons": [{"src": "/static/images/pwa/icon-192.png", "sizes": "192x192", "type": "image/png"}]
            },
            {
                "name": "Portail Gestion Direction",
                "short_name": "Gestion",
                "description": "Accès rapide Direction & Tableur Excel",
                "url": "/gestion/?source=pwa_shortcut",
                "icons": [{"src": "/static/images/pwa/icon-192.png", "sizes": "192x192", "type": "image/png"}]
            }
        ]
    }
    return JsonResponse(manifest, content_type='application/manifest+json; charset=utf-8')


def pwa_service_worker(request):
    """Service Worker v3 Pro : Stratégie hybride Réseau-Prioritaire + Cache Hors-Ligne + Streaming Vidéo."""
    from django.http import HttpResponse
    sw_js = """const CACHE_STATIC = 'onizuka-static-v3';
const CACHE_PAGES = 'onizuka-pages-v3';
const CACHE_IMAGES = 'onizuka-images-v3';
const ALL_CACHES = [CACHE_STATIC, CACHE_PAGES, CACHE_IMAGES];

const PRECACHE_URLS = [
  '/offline.html',
  '/static/css/main.css',
  '/static/js/capacitor-bridge.js',
  '/static/images/logo_icon.png',
  '/static/images/pwa/icon-192.png',
  '/static/images/pwa/icon-512.png',
  '/static/images/app-icon.svg'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_STATIC).then((cache) => cache.addAll(PRECACHE_URLS).catch(() => {}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => !ALL_CACHES.includes(k)).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  // Ne jamais intercepter les flux vidéo (Range requests iOS/Android) ni l'admin Django
  if (req.headers.has('range')) return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/media/products/videos/')) return;

  // 1. Fichiers statiques (CSS, JS, Icônes) -> Stale-While-Revalidate
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const networkFetch = fetch(req).then((res) => {
          if (res && res.status === 200) {
            const clone = res.clone();
            caches.open(CACHE_STATIC).then((c) => c.put(req, clone));
          }
          return res;
        }).catch(() => cached);
        return cached || networkFetch;
      })
    );
    return;
  }

  // 2. Photos produits (/media/products/ & /media/CACHE/) -> Cache-First avec rafraîchissement
  if (url.pathname.startsWith('/media/')) {
    event.respondWith(
      caches.open(CACHE_IMAGES).then((cache) =>
        cache.match(req).then((cached) => {
          const fetched = fetch(req).then((res) => {
            if (res && res.status === 200) {
              cache.put(req, res.clone());
            }
            return res;
          }).catch(() => cached);
          return cached || fetched;
        })
      )
    );
    return;
  }

  // 3. Navigation HTML publique -> Network-First avec secours Cache puis /offline.html
  const accept = req.headers.get('accept') || '';
  if (req.mode === 'navigate' || accept.includes('text/html')) {
    if (url.pathname.startsWith('/gestion/') || url.pathname.startsWith('/accounts/')) return;
    event.respondWith(
      fetch(req).then((res) => {
        if (res && res.status === 200 && !req.headers.get('HX-Request')) {
          const clone = res.clone();
          caches.open(CACHE_PAGES).then((c) => c.put(req, clone));
        }
        return res;
      }).catch(() =>
        caches.match(req).then((cached) => cached || caches.match('/offline.html'))
      )
    );
  }
});
"""
    response = HttpResponse(sw_js, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response




