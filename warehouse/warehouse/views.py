from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse

from django.shortcuts import redirect, get_object_or_404
from warehouse.models import ProductsProcessing, Product


def _redirect_to_with_error(request, url_name, object_id, message):
    messages.error(request, message)
    return redirect(reverse(url_name, args=[object_id]))


def _redirect_to_with_success(request, url_name, object_id, message):
    messages.success(request, message)
    return redirect(reverse(url_name, args=[object_id]))


@staff_member_required
def productsprocessing_close(request, object_id):
    change_url = "admin:warehouse_productsprocessing_change"

    products_processing = get_object_or_404(ProductsProcessing, pk=object_id)

    if products_processing.closed:
        return _redirect_to_with_error(request, change_url, object_id,
                                       "You cannot close Products Processing Entry which has been already closed")

    if products_processing.clean_for_processing():
        products_processing.close()
        products_processing.save()

        return _redirect_to_with_success(request, change_url, object_id,
                                         "Entry has been closed. Products quantities have been modified.")
    else:
        return _redirect_to_with_error(request, change_url, object_id,
                                       "Operation has been terminated due to the validation errors.")


@staff_member_required
def product_details(request, object_id):
    product = get_object_or_404(Product, pk=object_id)

    return JsonResponse({
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
        'currency': {
            'slug': product.currency.slug,
            'name': product.currency.name
        },
        'unit': {
            'slug': product.unit.slug,
            'name': product.unit.name
        }
    })