"""
ONIZOUKA SHOP - Views Paiements
Gestion Orange Money, Wave, Paiement a la livraison
"""
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from orders.models import Order
from orders.views import _get_accessible_order
from payments.models import Payment


def payment_process(request, order_number):
    """Page de paiement pour une commande"""
    order = _get_accessible_order(request, order_number)

    if order.payment_status:
        messages.info(request, 'Cette commande est déjà payée.')
        return redirect('orders:confirmation', order_number=order.order_number)

    context = {
        'order': order,
        'page_title': f'Paiement commande #{order.order_number} - Onizouka Shop',
    }
    return render(request, 'payments/process.html', context)


@require_POST
def payment_cash_on_delivery(request, order_number):
    """Confirmer paiement a la livraison"""
    order = _get_accessible_order(request, order_number)

    Payment.objects.update_or_create(
        order=order,
        defaults={
            'method': Order.PaymentMethod.CASH_ON_DELIVERY,
            'amount': order.total,
            'status': Payment.Status.PENDING,
        }
    )

    order.status = Order.Status.CONFIRMED
    order.payment_method = Order.PaymentMethod.CASH_ON_DELIVERY
    order.save(update_fields=['status', 'payment_method'])

    messages.success(request, f'Commande #{order.order_number} confirmée avec paiement à la livraison.')
    return redirect('orders:confirmation', order_number=order.order_number)


def payment_success(request, order_number):
    """Enregistrement de la référence de dépôt transmise par le client (Orange Money / Wave)"""
    order = _get_accessible_order(request, order_number)

    reference = (request.POST.get('payment_reference') or request.GET.get('payment_reference') or '').strip()
    raw_method = (request.POST.get('payment_method') or request.GET.get('payment_method') or order.payment_method).strip()
    if raw_method == 'cash_on_delivery':
        raw_method = Order.PaymentMethod.CASH_ON_DELIVERY
    valid_methods = {code for code, _ in Order.PaymentMethod.choices}
    method = raw_method if raw_method in valid_methods else order.payment_method

    if reference:
        order.payment_reference = reference
    if method:
        order.payment_method = method

    order.save(update_fields=['payment_reference', 'payment_method'])

    Payment.objects.update_or_create(
        order=order,
        defaults={
            'method': order.payment_method,
            'amount': order.total,
            'status': Payment.Status.PENDING,
            'transaction_id': order.payment_reference,
        }
    )

    messages.success(
        request,
        "Référence de transaction enregistrée avec succès. Notre équipe vérifie votre dépôt au Grand Marché (+223 92 67 37 99)."
    )
    return redirect('orders:confirmation', order_number=order.order_number)


def payment_failure(request, order_number):
    """Callback echec de paiement"""
    order = _get_accessible_order(request, order_number)
    messages.error(request, 'Le paiement a échoué. Veuillez réessayer.')
    return redirect('payments:process', order_number=order.order_number)
