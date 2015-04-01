from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.db import transaction
from warehouse.models import ProductsProcessing, Product
from warehouse.forms import ReviewForm

from wkhtmltopdf.views import PDFTemplateView

import reversion


def _redirect_to_with_error(request, url_name, object_id, message):
    messages.error(request, message)

    if object_id is not None:
        return redirect(reverse(url_name, args=[object_id]))
    else:
        return redirect(reverse(url_name))


def _redirect_to_with_success(request, url_name, object_id, message):
    messages.success(request, message)

    if object_id is not None:
        return redirect(reverse(url_name, args=[object_id]))
    else:
        return redirect(reverse(url_name))


@staff_member_required
def productsprocessing_close(request, object_id):
    change_url = "admin:warehouse_productsprocessing_change"

    products_processing = get_object_or_404(ProductsProcessing, pk=object_id)

    if products_processing.closed:
        return _redirect_to_with_error(request, change_url, object_id,
                                        "You cannot close Products Processing Entry which has been already closed")

    if products_processing.clean_for_processing():
        with transaction.atomic(), reversion.create_revision():
            products_processing.close()
            products_processing.save()
            reversion.set_user(request.user)
            reversion.set_comment("Processing closed")

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
        'unit': {
            'slug': product.unit.slug,
            'name': product.unit.name
        }
    })


@staff_member_required
def monthly_review(request):
    return render(request, "warehouse/productsprocessing/review/review.html", {
        'reviews': [{'date': "{}-{}-01".format(review[0], str(review[1]).zfill(2)), 'text': "{}/{}".format(review[0], str(review[1]).zfill(2))} for review in ProductsProcessing.objects.reviews()],
        'opts': {
            'app_label': 'warehouse',
            'app_config': {
                'verbose_name': 'Warehouse'
            }
        }
    });

class MonthlyReviewPDF(PDFTemplateView):
    filename = "review.pdf"
    template_name = "warehouse/productsprocessing/review/pdf/review.html"

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(MonthlyReviewPDF, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = ReviewForm({'date': args[0]})

        if form.is_valid():
            selected_date = form.cleaned_data['date']
            month = selected_date.month
            year = selected_date.year

            processings = ProductsProcessing.objects.review_for_month(year=year, month=month)
            
            kwargs['processings'] = processings

            return super(MonthlyReviewPDF, self).get(request, *args, **kwargs)
        else:
            return _redirect_to_with_error(
                    request,
                    'admin:warehouse_productsprocessing_changelist',
                    None,
                    "Specified review could not be generated."
                )
