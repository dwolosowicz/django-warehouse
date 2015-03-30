from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import productsprocessing_close, product_details, monthly_review, MonthlyReviewPDF

urlpatterns = patterns('',
    # Custom admin actions
    url(r'^warehouse/product/(\d+)/details/$', product_details, name="warehouse_product_details"),
    url(r'^warehouse/productsprocessing/(\d+)/close/$', productsprocessing_close, name="warehouse_productsprocessing_close"),
    url(r'^warehouse/productsprocessing/review/$', monthly_review, name="warehouse_productsprocessing_review"),
    url(r'^warehouse/productsprocessing/review/(\d+-\d+-01)/$', MonthlyReviewPDF.as_view(), name="warehouse_productsprocessing_review_pdf"),

    # Default admin implementations
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^', include(admin.site.urls)),
)
