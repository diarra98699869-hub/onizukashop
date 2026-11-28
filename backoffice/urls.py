"""
ONIZUKA SHOP - URLs Backoffice Direction (/gestion/)
"""
from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    # Tableau de bord principal
    path('', views.dashboard_view, name='dashboard'),
    
    # Gestion des commandes & Caisse Express Boutique/WhatsApp
    path('commandes/', views.orders_view, name='orders'),
    path('commandes/nouvelle/', views.pos_order_create_view, name='order_create_pos'),
    path('commandes/export-csv/', views.export_orders_csv_view, name='export_orders_csv'),
    path('commandes/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('commandes/<int:order_id>/supprimer/', views.order_delete_view, name='order_delete'),
    path('commandes/<int:order_id>/action-rapide/', views.order_quick_list_action_view, name='order_quick_action'),
    path('commandes/<int:order_id>/facture/', views.order_invoice_view, name='order_invoice'),
    path('commandes/<int:order_id>/status-htmx/', views.update_order_status_htmx, name='order_status_htmx'),

    # Catalogue & Produits
    path('produits/', views.products_view, name='products'),
    path('produits/tableur/', views.products_bulk_edit_view, name='products_bulk_edit'),
    path('produits/sauvegarder-masse/', views.products_bulk_save_view, name='products_bulk_save'),
    path('produits/action-masse/', views.products_bulk_action_view, name='products_bulk_action'),
    path('produits/ajout-masse/', views.products_bulk_create_view, name='products_bulk_create'),
    path('produits/<int:product_id>/upload-image-rapide/', views.product_quick_image_upload_view, name='product_quick_image_upload'),
    path('produits/compresser-video/', views.product_video_compress_api_view, name='product_video_compress_api'),
    path('produits/export-csv/', views.export_products_csv_view, name='export_products_csv'),
    path('produits/modele-csv/', views.download_product_template_csv_view, name='product_template_csv'),
    path('produits/import-csv/', views.import_products_csv_view, name='import_products_csv'),
    path('produits/nouveau/', views.product_create_view, name='product_create'),
    path('produits/<int:product_id>/modifier/', views.product_edit_view, name='product_edit'),
    path('produits/<int:product_id>/supprimer/', views.product_delete_view, name='product_delete'),
    path('produits/<int:product_id>/rapide/', views.product_quick_update_view, name='product_quick_update'),
    path('produits/<int:product_id>/supprimer-image/<int:image_id>/', views.product_delete_image_view, name='product_delete_image'),
    path('produits/<int:product_id>/image-principale/<int:image_id>/', views.product_set_primary_image_view, name='product_set_primary_image'),
    path('produits/<int:product_id>/toggle-active/', views.product_toggle_active_htmx, name='product_toggle_active'),

    # Centre de contrôle Rayons, Marques, Codes Promo, Avis & Fournisseurs
    path('catalogue-config/', views.catalog_config_view, name='catalog_config'),

    # Centre de contrôle Emails, Templates, Conditions d'Envoi, Alertes & Rappels
    path('emails/', views.emails_center_view, name='emails_center'),
    path('emails/apercu/<str:template_key>/', views.email_template_preview_view, name='email_template_preview'),

    # Stocks, Arrivages, Déstockage & Inventaire
    path('stocks/', views.stocks_view, name='stocks'),
    path('stocks/ajuster-htmx/<int:product_id>/', views.stock_quick_adjust_htmx, name='stock_quick_adjust_htmx'),
    path('stocks/sortie/', views.stock_out_view, name='stock_out'),
    path('stocks/export-csv/', views.export_stocks_csv_view, name='export_stocks_csv'),
    path('stocks/fiche-inventaire/', views.stocks_inventory_sheet_view, name='stocks_inventory_sheet'),

    # Clients & Carnet d'adresses
    path('clients/', views.clients_view, name='clients'),
    path('clients/<int:client_id>/', views.client_detail_view, name='client_detail'),

    # Paramètres de l'Entreprise & Boutique
    path('parametres/', views.settings_view, name='settings'),

    # Utilisateurs, Équipe & Rôles
    path('utilisateurs/', views.users_view, name='users'),
    path('utilisateurs/nouveau/', views.user_create_view, name='user_create'),
    path('utilisateurs/<int:user_id>/modifier-role/', views.user_edit_role_view, name='user_edit_role'),
    path('utilisateurs/<int:user_id>/supprimer/', views.user_delete_view, name='user_delete'),
    path('utilisateurs/<int:user_id>/toggle-status/', views.user_toggle_status_view, name='user_toggle_status'),
    path('utilisateurs/<int:user_id>/impersonate/', views.user_impersonate_view, name='user_impersonate'),
    path('quitter-impersonation/', views.stop_impersonate_view, name='stop_impersonate'),
]
