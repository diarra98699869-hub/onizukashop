"""
ONIZOUKA SHOP - URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import RedirectView

import os
import mimetypes
from django.http import FileResponse, Http404, HttpResponse

def serve_media(request, path):
    file_path = os.path.join(str(settings.MEDIA_ROOT), path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')
    raise Http404("Media not found")

from django.urls import re_path
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from shop.views import robots_txt

sitemaps = {
    'produits': ProductSitemap,
    'categories': CategorySitemap,
    'pages': StaticViewSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('google7d4d405b790d11a0.html', lambda r: HttpResponse('google-site-verification: google7d4d405b790d11a0.html', content_type='text/html')),
    re_path(r'^media/(?P<path>.*)$', serve_media, name='serve_media'),
    path('admin/', admin.site.urls),
    path('gestion/', include('backoffice.urls', namespace='backoffice')),
    path('accounts/', include('allauth.urls')),
    path('compte/', include('accounts.urls', namespace='accounts')),
    path('panier/', include('orders.urls', namespace='orders')),
    path('paiement/', include('payments.urls', namespace='payments')),
    # Redirections transparentes de l'ancien préfixe /boutique/
    path('boutique/', RedirectView.as_view(url='/', permanent=False)),
    path('boutique/<path:subpath>', RedirectView.as_view(url='/%(subpath)s', permanent=False)),
    path('', include('shop.urls', namespace='shop')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)