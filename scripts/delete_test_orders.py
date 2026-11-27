import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
django.setup()

from orders.models import Order

# Numéros des commandes de test visibles sur la capture
test_numbers = ['ONZ36075018', 'ONZ50008393', 'ONZ71662496', 'ONZ33853443']

# Trouver les commandes à supprimer (par numéro ou téléphone de test)
orders_to_delete = Order.objects.filter(
    order_number__in=test_numbers
) | Order.objects.filter(delivery_phone__icontains='66826207')

print(f"Trouvé {orders_to_delete.count()} commandes de test à supprimer.")

deleted_count = 0
for order in orders_to_delete:
    print(f"\n[-] Traitement commande #{order.order_number} ({order.delivery_name} - {order.delivery_phone})")
    
    # 1. Restituer le stock pour chaque article
    for item in order.items.all():
        if item.product and item.product.track_stock:
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
            print(f"    -> Stock restitué pour '{item.product.name}': +{item.quantity} (nouveau stock: {item.product.stock})")
    
    # 2. Supprimer la commande (cascade sur items, paiements, logs)
    order_num = order.order_number
    order.delete()
    deleted_count += 1
    print(f"    [OK] Commande #{order_num} supprimée définitivement.")

print(f"\nNettoyage terminé : {deleted_count} commandes de test supprimées avec succès.")
