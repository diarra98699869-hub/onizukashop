"""
ONIZOUKA SHOP - Modeles de donnees
App: shop
Contient: Category, Brand, Product, ProductImage, Review
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import MPTTModel, TreeForeignKey
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill


class Category(MPTTModel):
    """Categories hierarchiques (arbre infini avec MPTT)"""
    name = models.CharField(max_length=200, verbose_name='Nom')
    slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', verbose_name='Categorie parente')
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name='Image')
    description = models.TextField(blank=True, verbose_name='Description')
    icon = models.CharField(max_length=50, blank=True, help_text='Material Icons name', verbose_name='Icone')
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta titre SEO')
    meta_description = models.TextField(max_length=500, blank=True, verbose_name='Meta description SEO')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['order', 'name']

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})

    def get_products_count(self):
        return self.products.filter(is_active=True).count()

    @property
    def short_name(self):
        """Nom concis pour les barres de navigation mobile et onglets"""
        short_map = {
            'congelateurs-horizontaux': 'Congélateurs Coffres',
            'congelateurs-verticaux': 'Congélateurs Verticaux',
            'vitrines-refrigerees': 'Vitrines Réfrigérées',
            'climatiseurs': 'Climatiseurs',
            'climatisation': 'Ventilation & Solaire',
            'refrigerateurs': 'Réfrigérateurs',
            'televiseurs': 'Téléviseurs & TV',
            'cuisinieres': 'Cuisinières',
            'petit-electromenager': 'Petit Électro',
            'meubles-armoires': 'Armoires & Meubles',
            'meubles': 'Meubles',
            'mobilier': 'Mobilier',
            'decoration': 'Déco & Design',
            'literie': 'Literie',
            'salon': 'Salons',
            'bureau': 'Bureau',
            'solaire': 'Solaire',
        }
        for key, val in short_map.items():
            if key in self.slug:
                return val
        if '&' in self.name:
            return self.name.split('&')[0].strip()
        return self.name


class Brand(models.Model):
    """Marques des produits (Samsung, LG, Haier, etc.)"""
    name = models.CharField(max_length=100, verbose_name='Nom')
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, verbose_name='Logo')
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Marque'
        verbose_name_plural = 'Marques'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Produit electronique (frigo, clim, TV, etc.)"""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        INACTIVE = 'inactive', 'Inactif'
        OUT_OF_STOCK = 'out_of_stock', 'Rupture de stock'
        COMING_SOON = 'coming_soon', 'Prochainement'

    # Infos de base
    name = models.CharField(max_length=300, verbose_name='Nom du produit')
    slug = models.SlugField(max_length=300, unique=True, verbose_name='URL slug')
    sku = models.CharField(max_length=100, unique=True, verbose_name='Reference SKU')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products',
                                 verbose_name='Categorie')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='products', verbose_name='Marque')

    # Description
    short_description = models.TextField(max_length=500, blank=True, verbose_name='Description courte')
    description = models.TextField(verbose_name='Description complete')
    specifications = models.JSONField(default=dict, blank=True,
                                      help_text='Specs techniques en JSON {"Capacite": "350L", "Classe": "A+++"}',
                                      verbose_name='Specifications techniques')

    # Prix
    price = models.DecimalField(max_digits=12, decimal_places=0,
                                validators=[MinValueValidator(0)],
                                verbose_name='Prix normal (FCFA)')
    sale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True,
                                     validators=[MinValueValidator(0)],
                                     verbose_name='Prix promo (FCFA)')
    cost_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True,
                                     validators=[MinValueValidator(0)],
                                     verbose_name='Prix de revient (FCFA)')

    # Stock
    stock = models.PositiveIntegerField(default=0, verbose_name='Quantite en stock')
    min_stock = models.PositiveIntegerField(default=5, verbose_name='Stock minimum (alerte)')
    track_stock = models.BooleanField(default=True, verbose_name='Gerer le stock')

    # Caracteristiques physiques & Média Vidéo
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                 verbose_name='Poids (kg)')
    dimensions = models.CharField(max_length=100, blank=True,
                                  help_text='LxlxH en cm', verbose_name='Dimensions')
    video_file = models.FileField(upload_to='products/videos/', blank=True, null=True,
                                  verbose_name='Vidéo du produit (MP4/MOV/WebM)')
    video_url = models.URLField(blank=True,
                                verbose_name='Lien vidéo externe (YouTube, TikTok ou MP4)')
    is_eco_solar = models.BooleanField(default=False,
                                       verbose_name='Éco-Énergie / Compatible Solaire')
    addon_label = models.CharField(max_length=120, blank=True,
                                   verbose_name='Option 1-clic (ex: Montage meuble, Installation clim, Stabilisateur)')
    addon_price = models.DecimalField(max_digits=10, decimal_places=0, default=0,
                                      validators=[MinValueValidator(0)],
                                      verbose_name='Prix de l\'option (FCFA)')

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='Meta titre SEO')
    meta_description = models.TextField(max_length=500, blank=True, verbose_name='Meta description SEO')

    # Statut et dates
    status = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.ACTIVE, verbose_name='Statut')
    is_active = models.BooleanField(default=True, verbose_name='Visible')
    is_featured = models.BooleanField(default=False, verbose_name='Produit vedette')
    is_new = models.BooleanField(default=True, verbose_name='Nouveau')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date creation')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Derniere modif')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            import uuid
            self.sku = f'ONZ-{uuid.uuid4().hex[:8].upper()}'
        # Mettre a jour le statut selon le stock
        if self.track_stock and self.stock == 0:
            self.status = self.Status.OUT_OF_STOCK
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Retourne le prix actuel (promo ou normal)"""
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de remise"""
        if self.sale_price and self.sale_price < self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return 0

    @property
    def is_on_sale(self):
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def stock_value(self):
        """Valeur financière marchande du stock disponible en FCFA"""
        return int((self.stock or 0) * (self.current_price or 0))

    @property
    def stock_status_info(self):
        """Renvoie le statut visuel du stock (label, couleur, jauge)"""
        if (self.stock or 0) <= 0:
            return {
                'label': 'Rupture',
                'full_label': '0 unité • Rupture',
                'badge_class': 'bg-rose-50 text-rose-700 border border-rose-200',
                'bar_color': 'bg-rose-500',
                'percent': 0,
                'code': 'out',
            }
        elif self.stock <= (self.min_stock or 5):
            pct = min(100, int((self.stock / max(1, (self.min_stock or 5) * 2)) * 100))
            return {
                'label': 'Stock bas',
                'full_label': f"{self.stock} unité{'s' if self.stock > 1 else ''} • Alerte",
                'badge_class': 'bg-amber-50 text-amber-900 border border-amber-300 font-black',
                'bar_color': 'bg-amber-500',
                'percent': max(18, pct),
                'code': 'low',
            }
        else:
            pct = min(100, int((self.stock / max(1, (self.min_stock or 5) * 3)) * 100))
            return {
                'label': 'En stock',
                'full_label': f"{self.stock} unités",
                'badge_class': 'bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold',
                'bar_color': 'bg-emerald-500',
                'percent': min(100, max(30, pct)),
                'code': 'ok',
            }

    @property
    def margin(self):
        """Marge bénéficiaire brute en FCFA (Prix de vente actuel - Prix d'achat)"""
        if self.cost_price:
            return int(self.current_price - self.cost_price)
        return None

    @property
    def margin_percentage(self):
        """Pourcentage de marge commerciale"""
        if self.cost_price and self.cost_price > 0:
            return round(((self.current_price - self.cost_price) / self.cost_price) * 100, 1)
        return None

    @property
    def is_in_stock(self):
        if not self.track_stock:
            return True
        return self.stock > 0

    @property
    def is_low_stock(self):
        return self.track_stock and 0 < self.stock <= self.min_stock

    @property
    def primary_image(self):
        """Retourne l'image principale du produit en exploitant le cache prefetch_related (0 requête N+1)"""
        imgs = list(self.images.all())
        if not imgs:
            return None
        for img in imgs:
            if img.is_primary:
                return img
        return imgs[0]

    @property
    def secondary_image(self):
        """Retourne la seconde image du produit si disponible (0 requête N+1)"""
        imgs = list(self.images.all())
        if len(imgs) > 1:
            primary = self.primary_image
            for img in imgs:
                if img != primary:
                    return img
        return None

    def get_average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def get_reviews_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_formatted_price(self):
        return f"{int(self.current_price):,} FCFA".replace(",", " ")

    def get_specifications_list(self):
        """Retourne les specs comme liste de tuples"""
        return list((self.specifications or {}).items())

    @property
    def has_video(self):
        return bool(self.video_file or self.video_url)

    @property
    def youtube_embed_url(self):
        """
        Extrait un lien embed propre et conforme aux normes de sécurité YouTube pour éviter l'erreur 153.
        Supporte :
        - Liens classiques : youtube.com/watch?v=... (avec paramètres multiples &t=, &feature=, app=desktop)
        - Liens courts : youtu.be/... (avec ?si=...)
        - Liens Shorts : youtube.com/shorts/...
        - Liens Mobile : m.youtube.com/...
        - Liens Live : youtube.com/live/...
        - Tags <iframe> complets collés par erreur
        - Identifiants bruts (11 caractères)
        """
        if not self.video_url:
            return ''
        import re
        from urllib.parse import urlparse, parse_qs

        raw = str(self.video_url).strip()

        # Si l'utilisateur a collé un tag iframe HTML complet
        if '<iframe' in raw.lower():
            m_src = re.search(r'src=["\']([^"\']+)["\']', raw)
            if m_src:
                raw = m_src.group(1).strip()

        video_id = None

        # 1. Extraction via query string (v=...)
        if 'watch' in raw or '?' in raw:
            try:
                parsed = urlparse(raw)
                qs = parse_qs(parsed.query)
                if 'v' in qs and qs['v'] and len(qs['v'][0]) >= 11:
                    video_id = qs['v'][0][:11]
            except Exception:
                pass

        # 2. Extraction via regex sur les formats youtu.be, /embed/, /shorts/, /live/
        if not video_id:
            patterns = [
                r'(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/(?:embed|shorts|live|v)\/)([A-Za-z0-9_-]{11})',
                r'[?&]v=([A-Za-z0-9_-]{11})',
                r'^([A-Za-z0-9_-]{11})$',
            ]
            for pat in patterns:
                m = re.search(pat, raw)
                if m:
                    video_id = m.group(1)
                    break

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}?rel=0&playsinline=1&enablejsapi=1"
        return ''

    @property
    def smart_addon(self):
        """Option 1-clic personnalisée ou suggérée intelligemment selon le rayon (Meubles, Clims, Frigos, TV)."""
        if self.addon_label and self.addon_price is not None:
            return {'label': self.addon_label, 'price': int(self.addon_price)}
        cat_text = f"{self.category.slug} {self.category.name}".lower() if self.category_id else ''
        if any(k in cat_text for k in ('clim', 'split')):
            return {'label': 'Pose & installation murale (Bamako)', 'price': 15000}
        if any(k in cat_text for k in ('meuble', 'mobilier', 'salon', 'lit', 'armoire', 'table', 'bureau')):
            return {'label': 'Montage & installation à domicile', 'price': 10000}
        if any(k in cat_text for k in ('frigo', 'refrig', 'congel', 'tele', 'tv')):
            return {'label': 'Régulateur / Stabilisateur anti-surtension', 'price': 15000}
        return None


class ProductImage(models.Model):
    """Images des produits (plusieurs par produit)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images', verbose_name='Produit')
    image = models.ImageField(upload_to='products/', verbose_name='Image')

    # Versions optimisees automatiques via django-imagekit
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(300, 300)],
                               format='WEBP',
                               options={'quality': 85})
    medium = ImageSpecField(source='image',
                            processors=[ResizeToFit(600, 600)],
                            format='WEBP',
                            options={'quality': 90})
    large = ImageSpecField(source='image',
                           processors=[ResizeToFit(1200, 1200)],
                           format='WEBP',
                           options={'quality': 92})

    alt_text = models.CharField(max_length=200, blank=True, verbose_name='Texte alternatif')
    is_primary = models.BooleanField(default=False, verbose_name='Image principale')
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        verbose_name = 'Image produit'
        verbose_name_plural = 'Images produits'
        ordering = ['-is_primary', 'order']

    def __str__(self):
        return f"Image de {self.product.name}"

    def save(self, *args, **kwargs):
        # Compression automatique WebP ultra-rapide (50-80ms) et optimisée pour serveur mutualisé
        if self.image and not str(self.image.name).lower().endswith('.webp'):
            try:
                from PIL import Image, ImageOps
                from io import BytesIO
                from django.core.files.base import ContentFile
                import os

                self.image.open()
                im = Image.open(self.image)
                im = ImageOps.exif_transpose(im)
                if im.mode not in ('RGB', 'RGBA'):
                    im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
                
                # Redimensionnement BILINEAR (10x plus véloce que LANCZOS sur photos smartphone)
                max_dim = 1200
                if im.width > max_dim or im.height > max_dim:
                    im.thumbnail((max_dim, max_dim), Image.Resampling.BILINEAR)

                buf = BytesIO()
                # method=0 est le mode d'encodage le plus rapide (évite les saturations CPU)
                im.save(buf, format='WEBP', quality=82, method=0)
                im.close()

                base_name = os.path.splitext(os.path.basename(self.image.name))[0]
                self.image.save(f"{base_name}.webp", ContentFile(buf.getvalue()), save=False)
            except Exception:
                pass

        # Si c'est la premiere image, la definir comme principale
        if not self.pk and not self.product.images.exists():
            self.is_primary = True
        # Une seule image principale par produit
        if self.is_primary:
            self.product.images.exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Review(models.Model):
    """Avis et notes des clients sur les produits"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews', verbose_name='Produit')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='reviews', verbose_name='Client')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Note (1-5)'
    )
    title = models.CharField(max_length=200, verbose_name='Titre de l\'avis')
    body = models.TextField(verbose_name='Contenu de l\'avis')
    is_verified = models.BooleanField(default=False, verbose_name='Achat verifie')
    is_approved = models.BooleanField(default=True, verbose_name='Approuve')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Un avis par produit par client

    def __str__(self):
        return f"Avis de {self.user.get_full_name()} sur {self.product.name} ({self.rating}/5)"

    def get_stars_range(self):
        return range(self.rating)

    def get_empty_stars_range(self):
        return range(5 - self.rating)


class Wishlist(models.Model):
    """Favoris et coups de cœur des clients"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name='Client')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_entries', verbose_name='Appareil favori')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.name}"