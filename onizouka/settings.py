"""
ONIZOUKA SHOP - Settings Django 5
E-commerce electronique ultra premium
Securise - Performant - Extensible
"""

import os
from pathlib import Path
from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = BASE_DIR / '.env'
if env_path.exists():
    repo = RepositoryEnv(env_path)
    for k, v in repo.data.items():
        os.environ[k] = v
    config = Config(repo)
else:
    from decouple import config

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-onizouka-changez-en-prod-2026')
DEBUG = config('DEBUG', default=True, cast=bool)

raw_hosts = config('ALLOWED_HOSTS', default='*')
ALLOWED_HOSTS = ['*']


raw_origins = config('CSRF_TRUSTED_ORIGINS', default='')
if raw_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in raw_origins.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

for origin in [
    'https://onizukashop.com',
    'http://onizukashop.com',
    'https://www.onizukashop.com',
    'http://www.onizukashop.com',
    'https://onizouka.danayaplus.com',
    'http://onizouka.danayaplus.com',
    'https://danayaplus.com',
    'http://danayaplus.com',
    'https://*.danayaplus.com',
    'http://*.danayaplus.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://localhost',
]:
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Support Reverse Proxy SSL (o2switch / cPanel / Apache / Passenger)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Configuration CSRF robuste et résiliente
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_FAILURE_VIEW = 'onizouka.views.csrf_failure'


INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'mptt',
    'imagekit',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_tailwind',
    'django_htmx',
    'shop',
    'orders',
    'accounts',
    'payments',
    'inventory',
    'analytics',
    'backoffice.apps.BackofficeConfig',
]

MIDDLEWARE = [
    'onizouka.middleware.PassengerSslMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'onizouka.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart_count',
                'shop.context_processors.categories_menu',
                'shop.context_processors.shop_settings',
                'shop.context_processors.wishlist_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'onizouka.wsgi.application'

DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
            'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=60, cast=int),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': config('DB_NAME', default='onizouka_db'),
            'USER': config('DB_USER', default=''),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default=''),
            'PORT': config('DB_PORT', default=''),
            'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=60, cast=int),
        }
    }

REDIS_URL = config('REDIS_URL', default='')


def _is_redis_reachable(redis_url: str) -> bool:
    """Vérifie en 50ms si le serveur Redis répond réellement (socket unix ou TCP)."""
    if not redis_url:
        return False
    try:
        import os, socket
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        if parsed.scheme == 'unix':
            sock_path = parsed.path
            if not sock_path or not os.path.exists(sock_path):
                return False
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.05)
            s.connect(sock_path)
            s.close()
            return True
        else:
            host = parsed.hostname or '127.0.0.1'
            port = parsed.port or 6379
            with socket.create_connection((host, port), timeout=0.05):
                return True
    except Exception:
        return False


if REDIS_URL and _is_redis_reachable(REDIS_URL):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
                'SOCKET_CONNECT_TIMEOUT': 1,
                'SOCKET_TIMEOUT': 1,
            },
            'KEY_PREFIX': 'onizouka',
            'TIMEOUT': 300,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'onizouka-cache',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'


SESSION_COOKIE_AGE = 60 * 60 * 24 * 30


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Bamako'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(config('MEDIA_ROOT', default=str(BASE_DIR / 'media')))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration Emails Transactionnels (Console en local, SMTP SSL en production)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend' if not DEBUG else 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='mail.onizukashop.com')
EMAIL_PORT = config('EMAIL_PORT', default=465, cast=int)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_TIMEOUT = 4
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='contact@onizukashop.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ONIZUKA SHOP <contact@onizukashop.com>')
SERVER_EMAIL = config('SERVER_EMAIL', default='contact@onizukashop.com')


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAccountAdapter'
LOGIN_REDIRECT_URL = 'accounts:login_redirect'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

UNFOLD = {
    'SITE_TITLE': 'Onizouka Shop',
    'SITE_HEADER': 'Onizouka Admin',
    'SITE_URL': '/',
    'SITE_SYMBOL': 'store',
    'THEME': lambda request: 'light',
    'DASHBOARD_CALLBACK': 'onizouka.dashboard.dashboard_callback',
    'SCRIPTS': [
        lambda request: '/static/js/admin_light.js',
    ],
    'COLORS': {
        'primary': {
            '50':  '254 252 232',
            '100': '254 249 195',
            '200': '254 240 138',
            '300': '253 224 71',
            '400': '250 204 21',
            '500': '234 179 8',
            '600': '202 138 4',
            '700': '161 98 7',
            '800': '133 77 14',
            '900': '113 63 18',
            '950': '66 32 6',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'navigation': [
            {
                'title': 'Tableau de bord',
                'separator': True,
                'items': [
                    {'title': 'Accueil', 'icon': 'dashboard', 'link': '/admin/'},
                ],
            },
            {
                'title': 'Catalogue',
                'separator': True,
                'items': [
                    {'title': 'Produits', 'icon': 'inventory_2', 'link': '/admin/shop/product/'},
                    {'title': 'Categories', 'icon': 'category', 'link': '/admin/shop/category/'},
                    {'title': 'Marques', 'icon': 'branding_watermark', 'link': '/admin/shop/brand/'},
                ],
            },
            {
                'title': 'Commerce',
                'separator': True,
                'items': [
                    {'title': 'Commandes', 'icon': 'receipt_long', 'link': '/admin/orders/order/'},
                    {'title': 'Paiements', 'icon': 'payments', 'link': '/admin/payments/payment/'},
                ],
            },
            {
                'title': 'Clients',
                'separator': True,
                'items': [
                    {'title': 'Utilisateurs', 'icon': 'group', 'link': '/admin/auth/user/'},
                    {'title': 'Avis', 'icon': 'star', 'link': '/admin/shop/review/'},
                ],
            },
            {
                'title': 'Stock',
                'separator': True,
                'items': [
                    {'title': 'Mouvements', 'icon': 'warehouse', 'link': '/admin/inventory/stockmovement/'},
                    {'title': 'Fournisseurs', 'icon': 'local_shipping', 'link': '/admin/inventory/supplier/'},
                ],
            },
        ],
    },
}

if not DEBUG:
    # Sur cPanel/o2switch, la redirection HTTPS est déjà gérée nativement par Apache/.htaccess
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SESSION_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django_error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

ORANGE_MONEY_API_KEY = config('ORANGE_MONEY_API_KEY', default='')
WAVE_API_KEY = config('WAVE_API_KEY', default='')
CINETPAY_API_KEY = config('CINETPAY_API_KEY', default='')
CINETPAY_SITE_ID = config('CINETPAY_SITE_ID', default='')

CURRENCY = 'FCFA'
SHOP_NAME = 'Onizouka Shop'
SHOP_TAGLINE = "L'electronique de qualite au Mali"
PRODUCTS_PER_PAGE = 24
LOW_STOCK_THRESHOLD = 5

# ==============================================================================
# PERFORMANCE & CACHE IMAGES (Optimistic ImageKit - Pas de checks disques redondants)
# ==============================================================================
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'
IMAGEKIT_SPEC_CACHEFILE_NAMER = 'imagekit.cachefiles.namers.hash'
IMAGEKIT_CACHEFILE_DIR = 'CACHE/images'
