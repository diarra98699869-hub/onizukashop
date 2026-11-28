"""
ONIZUKA SHOP - URLs du shop
"""
from django.urls import path
from shop import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalog, name='catalog'),
    path('catalogue/<slug:slug>/', views.category_detail, name='catalog_category'),
    path('recherche/', views.search, name='search'),
    path('recherche/live/', views.live_search, name='live_search'),
    path('categorie/<slug:slug>/', views.category_detail, name='category'),
    path('produit/<slug:slug>/', views.product_detail, name='product'),
    path('produit/<slug:slug>/avis/', views.add_review, name='add_review'),
    path('favoris/', views.wishlist_view, name='wishlist'),
    path('favoris/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('contact/', views.contact, name='contact'),
    path('cgv/', views.terms_view, name='terms'),
    path('confidentialite/', views.privacy_view, name='privacy'),
    path('mentions-legales/', views.legal_view, name='legal'),
    path('livraison-garantie/', views.shipping_warranty_view, name='shipping_warranty'),
    path('facebook-catalog.xml', views.facebook_catalog_feed, name='facebook_catalog'),
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.pwa_service_worker, name='pwa_sw'),
    path('offline.html', views.pwa_offline_view, name='pwa_offline'),
]
