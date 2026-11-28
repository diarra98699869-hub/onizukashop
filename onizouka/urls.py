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
from pathlib import Path
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden

BLOCKED_MEDIA_EXTENSIONS = {
    '.py', '.pyc', '.php', '.phtml', '.phar', '.sh', '.bash', '.exe', '.bat',
    '.cmd', '.ps1', '.sqlite3', '.sqlite', '.sql', '.env', '.htaccess', '.html', '.htm',
}

def serve_media(request, path):
    media_root = Path(settings.MEDIA_ROOT).resolve()
    try:
        target = (media_root / path).resolve()
        is_inside = target.is_relative_to(media_root)
    except Exception:
        is_inside = False
        target = None

    if not is_inside or target is None:
        from onizouka.security_shield import collect_forensic_summary, record_and_alert_intrusion, _forbidden_shield_response
        summary = collect_forensic_summary(
            request,
            attack_type="Tentative d'évasion de répertoire Media (Path Traversal)",
            details=f"Tentative d'accès hors de MEDIA_ROOT via le chemin : '{path}'",
            severity='critical',
            action_taken="Accès fichier bloqué (HTTP 403)",
        )
        record_and_alert_intrusion(summary)
        return _forbidden_shield_response(summary['incident_id'])

    if target.suffix.lower() in BLOCKED_MEDIA_EXTENSIONS:
        return HttpResponseForbidden("Forbidden media type.")

    if target.exists() and target.is_file():
        content_type, _ = mimetypes.guess_type(str(target))
        resp = FileResponse(open(target, 'rb'), content_type=content_type or 'application/octet-stream')
        resp['X-Content-Type-Options'] = 'nosniff'
        if target.suffix.lower() == '.svg':
            resp['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'; sandbox"
        return resp
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