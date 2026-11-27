"""
ONIZOUKA SHOP - Formulaires du Backoffice Professionnel (Optimisés Mobile & Tactile)
"""
from django import forms
from shop.models import Product, Category, Brand
from orders.models import Order
from inventory.models import Supplier

INPUT_CLS = (
    'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white '
    'focus:border-amber-500 focus:ring-2 focus:ring-amber-500/15 outline-none '
    'text-base sm:text-sm text-slate-900 placeholder:text-slate-400 transition'
)
SELECT_CLS = (
    'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white '
    'focus:border-amber-500 focus:ring-2 focus:ring-amber-500/15 outline-none '
    'text-base sm:text-sm font-medium text-slate-900 transition'
)
CHECK_CLS = 'w-5 h-5 text-amber-500 rounded border-slate-300 focus:ring-amber-500 cursor-pointer'


class ProductForm(forms.ModelForm):
    """Formulaire complet et rapide d'ajout / modification de produit (compatible saisie express mobile)."""
    new_category_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLS,
            'placeholder': 'Ex: Congélateurs Solaires'
        })
    )
    new_brand_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLS,
            'placeholder': 'Ex: Roch, Nasco, Hisense...'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'brand', 'price', 'sale_price', 'cost_price',
            'stock', 'min_stock', 'track_stock', 'status', 'is_active', 'is_featured', 'is_new',
            'is_eco_solar', 'video_url', 'addon_label', 'addon_price',
            'short_description', 'description', 'dimensions', 'weight'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLS + ' font-semibold',
                'placeholder': 'Ex: Salon Cuir 7 Places, Lustre Cristal LED, Frigo Samsung 350L...'
            }),
            'sku': forms.TextInput(attrs={
                'class': INPUT_CLS + ' font-mono uppercase',
                'placeholder': 'Auto-généré si laissé vide (ex: ONZ-CLM-001)'
            }),
            'category': forms.Select(attrs={'class': SELECT_CLS}),
            'brand': forms.Select(attrs={'class': SELECT_CLS}),
            'price': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-bold font-mono',
                'placeholder': 'Ex: 450000',
                'inputmode': 'numeric'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-mono',
                'placeholder': 'Optionnel (prix remisé)',
                'inputmode': 'numeric'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-mono',
                'placeholder': 'Optionnel (confidentiel)',
                'inputmode': 'numeric'
            }),
            'stock': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-bold font-mono',
                'inputmode': 'numeric'
            }),
            'min_stock': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-mono',
                'inputmode': 'numeric'
            }),
            'track_stock': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'status': forms.Select(attrs={'class': SELECT_CLS}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'is_featured': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'is_new': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'is_eco_solar': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'video_url': forms.URLInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'Optionnel : lien YouTube, Shorts ou MP4 externe'
            }),
            'addon_label': forms.TextInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'Ex: Montage à domicile, Pose murale, Stabilisateur...'
            }),
            'addon_price': forms.NumberInput(attrs={
                'class': INPUT_CLS + ' font-mono',
                'placeholder': 'Ex: 10000',
                'inputmode': 'numeric'
            }),
            'short_description': forms.Textarea(attrs={
                'class': INPUT_CLS,
                'rows': 2,
                'placeholder': 'Points clés courts (matière, dimensions, garantie, finition...)'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLS,
                'rows': 4,
                'placeholder': 'Caractéristiques complètes (optionnel : généré automatiquement si laissé vide)'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'Ex: 240 x 160 x 85 cm'
            }),
            'weight': forms.NumberInput(attrs={
                'class': INPUT_CLS,
                'placeholder': 'Ex: 45'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sku'].required = False
        self.fields['category'].required = False
        self.fields['description'].required = False
        self.fields['addon_price'].required = False
        if not self.instance.pk:
            self.fields['stock'].initial = 5
            self.fields['is_active'].initial = True
            self.fields['is_new'].initial = True
            self.fields['addon_price'].initial = 0

    def clean(self):
        cleaned = super().clean()
        new_cat = (cleaned.get('new_category_name') or '').strip()
        cat = cleaned.get('category')
        if new_cat:
            from django.utils.text import slugify
            slug = slugify(new_cat) or 'rayon'
            cat_obj, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': new_cat, 'is_active': True}
            )
            cleaned['category'] = cat_obj
        elif not cat:
            self.add_error('category', 'Choisissez une catégorie ou créez-en une nouvelle.')

        new_brand = (cleaned.get('new_brand_name') or '').strip()
        if new_brand:
            from django.utils.text import slugify
            slug = slugify(new_brand) or 'marque'
            brand_obj, _ = Brand.objects.get_or_create(
                slug=slug,
                defaults={'name': new_brand, 'is_active': True}
            )
            cleaned['brand'] = brand_obj

        if not (cleaned.get('description') or '').strip():
            short = (cleaned.get('short_description') or '').strip()
            name = (cleaned.get('name') or 'Appareil certifié Onizouka Shop').strip()
            cleaned['description'] = short if short else f"{name} — Disponible au Grand Marché de Bamako (Dibidani) avec garantie officielle."

        return cleaned


class StockSupplyForm(forms.Form):
    """Formulaire d'approvisionnement rapide de stock"""
    product_id = forms.IntegerField()
    quantity = forms.IntegerField(
        min_value=1,
        initial=5,
        widget=forms.NumberInput(attrs={
            'class': INPUT_CLS + ' font-bold font-mono',
            'placeholder': 'Quantité reçue',
            'inputmode': 'numeric'
        })
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True),
        required=False,
        empty_label="Sélectionner un fournisseur (optionnel)",
        widget=forms.Select(attrs={'class': SELECT_CLS})
    )
    reference = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLS,
            'placeholder': 'Ex: Arrivage conteneur / BL-042'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLS,
            'placeholder': 'Note interne (optionnel)'
        })
    )


class OrderUpdateForm(forms.ModelForm):
    """Mise à jour complète d'une commande depuis la gestion (statut, paiement, livraison, remise)."""
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'payment_method', 'payment_reference',
            'delivery_name', 'delivery_phone', 'delivery_email', 'delivery_city', 'delivery_district', 'delivery_address',
            'delivery_fee', 'discount', 'admin_notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': SELECT_CLS}),
            'payment_status': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'payment_method': forms.Select(attrs={'class': SELECT_CLS}),
            'payment_reference': forms.TextInput(attrs={
                'class': INPUT_CLS + ' font-mono',
                'placeholder': 'ID transaction SMS Orange Money / Wave'
            }),
            'delivery_name': forms.TextInput(attrs={'class': INPUT_CLS + ' font-semibold'}),
            'delivery_phone': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'inputmode': 'tel'}),
            'delivery_email': forms.EmailInput(attrs={'class': INPUT_CLS, 'placeholder': 'client@gmail.com'}),
            'delivery_city': forms.TextInput(attrs={'class': INPUT_CLS}),
            'delivery_district': forms.TextInput(attrs={'class': INPUT_CLS, 'placeholder': 'Quartier Bamako'}),
            'delivery_address': forms.Textarea(attrs={'class': INPUT_CLS, 'rows': 2}),
            'delivery_fee': forms.NumberInput(attrs={'class': INPUT_CLS + ' font-mono font-bold', 'inputmode': 'numeric'}),
            'discount': forms.NumberInput(attrs={'class': INPUT_CLS + ' font-mono font-bold text-emerald-700', 'inputmode': 'numeric'}),
            'admin_notes': forms.Textarea(attrs={
                'class': INPUT_CLS,
                'rows': 2,
                'placeholder': 'Notes internes (livreur, heure souhaitée, confirmation client...)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname in ('payment_method', 'payment_reference', 'delivery_name', 'delivery_phone', 'delivery_email', 'delivery_city', 'delivery_district', 'delivery_address', 'delivery_fee', 'discount'):
            if fname in self.fields:
                self.fields[fname].required = False


class ShopSettingForm(forms.ModelForm):
    """Formulaire de configuration générale de la boutique et de l'entreprise."""
    class Meta:
        from .models import ShopSetting
        model = ShopSetting
        fields = [
            'site_name', 'company_name', 'nif', 'rccm', 'address',
            'phone_contact', 'phone_whatsapp', 'email_contact', 'email_orders',
            'currency', 'default_delivery_fee', 'free_delivery_threshold', 'delivery_delay_text', 'store_pickup_active',
            'orange_money_number', 'wave_number', 'cash_on_delivery_active',
            'default_min_stock_alert', 'block_order_on_out_of_stock',
            'email_notifications_active', 'whatsapp_notifications_active',
            'flash_sale_active', 'flash_sale_title', 'flash_sale_subtitle', 'flash_sale_end_date',
            'meta_pixel_id', 'meta_domain_verification'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={'class': INPUT_CLS + ' font-semibold'}),
            'company_name': forms.TextInput(attrs={'class': INPUT_CLS}),
            'nif': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono'}),
            'rccm': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono'}),
            'address': forms.TextInput(attrs={'class': INPUT_CLS}),
            'phone_contact': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'inputmode': 'tel'}),
            'phone_whatsapp': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'inputmode': 'tel'}),
            'email_contact': forms.EmailInput(attrs={'class': INPUT_CLS}),
            'email_orders': forms.EmailInput(attrs={'class': INPUT_CLS}),
            'currency': forms.TextInput(attrs={'class': INPUT_CLS + ' font-bold'}),
            'default_delivery_fee': forms.NumberInput(attrs={'class': INPUT_CLS + ' font-bold font-mono', 'inputmode': 'numeric'}),
            'free_delivery_threshold': forms.NumberInput(attrs={'class': INPUT_CLS + ' font-bold font-mono', 'inputmode': 'numeric'}),
            'delivery_delay_text': forms.TextInput(attrs={'class': INPUT_CLS}),
            'orange_money_number': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'inputmode': 'tel'}),
            'wave_number': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'inputmode': 'tel'}),
            'default_min_stock_alert': forms.NumberInput(attrs={'class': INPUT_CLS + ' font-bold font-mono', 'inputmode': 'numeric'}),
            'store_pickup_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'cash_on_delivery_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'block_order_on_out_of_stock': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'email_notifications_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'whatsapp_notifications_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'flash_sale_active': forms.CheckboxInput(attrs={'class': CHECK_CLS}),
            'flash_sale_title': forms.TextInput(attrs={'class': INPUT_CLS + ' font-semibold'}),
            'flash_sale_subtitle': forms.TextInput(attrs={'class': INPUT_CLS}),
            'flash_sale_end_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': INPUT_CLS + ' font-mono'}
            ),
            'meta_pixel_id': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'placeholder': 'Ex: 123456789012345'}),
            'meta_domain_verification': forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'placeholder': 'Ex: 1a2b3c4d5e6f7g8h9i0j'}),
        }


class UserCreateForm(forms.Form):
    """Création d'un nouvel utilisateur ou collaborateur depuis la Direction."""
    ROLE_CHOICES = [
        ('direction', 'Direction Générale (Super-Administrateur IT)'),
        ('gestionnaire', 'Gestionnaire Commercial & Stocks (Staff Direction)'),
        ('client', 'Client Acheteur Standard'),
    ]

    username = forms.CharField(
        label="Identifiant de connexion",
        max_length=150,
        widget=forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono'})
    )
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS})
    )
    last_name = forms.CharField(
        label="Nom de famille",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS})
    )
    email = forms.EmailField(
        label="Adresse Email",
        widget=forms.EmailInput(attrs={'class': INPUT_CLS})
    )
    phone = forms.CharField(
        label="Numéro de Téléphone (Mali)",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'placeholder': '+223 ...', 'inputmode': 'tel'})
    )
    role = forms.ChoiceField(
        label="Rôle et niveau d'accès",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLS})
    )
    password = forms.CharField(
        label="Mot de passe initial",
        widget=forms.PasswordInput(attrs={'class': INPUT_CLS})
    )


class UserEditRoleForm(forms.Form):
    """Modification du rôle et des permissions d'un utilisateur par la Direction."""
    ROLE_CHOICES_STAFF = [
        ('gestionnaire', 'Gestionnaire Direction (Accès Backoffice ERP)'),
        ('client', 'Client Acheteur Standard (Accès Boutique uniquement)'),
    ]
    ROLE_CHOICES_SUPERUSER = [
        ('direction', 'Super-Administrateur Technique (Contrôle Total)'),
        ('gestionnaire', 'Gestionnaire Direction (Accès Backoffice ERP)'),
        ('client', 'Client Acheteur Standard (Accès Boutique uniquement)'),
    ]

    first_name = forms.CharField(label="Prénom", max_length=150, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLS}))
    last_name = forms.CharField(label="Nom de famille", max_length=150, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLS}))
    email = forms.EmailField(label="Adresse Email", widget=forms.EmailInput(attrs={'class': INPUT_CLS}))
    phone = forms.CharField(label="Téléphone Mali", max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLS + ' font-mono', 'placeholder': '+223 ...', 'inputmode': 'tel'}))
    role = forms.ChoiceField(label="Rôle attribué", choices=ROLE_CHOICES_STAFF, widget=forms.Select(attrs={'class': SELECT_CLS}))

    def __init__(self, *args, is_superuser=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = self.ROLE_CHOICES_SUPERUSER if is_superuser else self.ROLE_CHOICES_STAFF
