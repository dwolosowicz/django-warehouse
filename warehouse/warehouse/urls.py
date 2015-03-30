from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import productsprocessing_close, product_details

urlpatterns = patterns('',
    # Custom admin actions
    url(r'^warehouse/product/(\d+)/details/$', product_details, name="warehouse_product_details"),
    url(r'^warehouse/productsprocessing/(\d+)/close/$', productsprocessing_close, name="warehouse_productsprocessing_close"),

    # Default admin implementations
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^', include(admin.site.urls)),
)
