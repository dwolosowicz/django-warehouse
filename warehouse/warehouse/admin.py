import resource
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

from .models import Warehouse, Product, Unit, ProductsProcessing, ProductProcessingNode, Currency
from .admin_mixins import ModedInlinesMixin, ReadOnlyEditFieldsMixin

admin.site.register(Unit)


@admin.register(Currency)
class CurrencyAdmin(ReadOnlyEditFieldsMixin, admin.ModelAdmin):
    readonly_edit_fields = ('name', 'slug')

    def has_add_permission(self, request):
        return False


@admin.register(Product)
class ProductAdmin(ReadOnlyEditFieldsMixin, admin.ModelAdmin):
    fields = ('warehouses', 'name', 'price', 'currency', 'quantity', 'unit')
    list_display = ('name', 'cost', 'amount', 'reservation_amount')
    list_editable = ('name',)
    exclude = ('deleted',)

    readonly_edit_fields = ('quantity', 'unit')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'products_count')


class ProductProcessingNodeInlineAdmin(admin.TabularInline):

    class Media:
        js = (
            'warehouse/js/node_inline_admin.js',
        )

    model = ProductProcessingNode
    template = "admin/warehouse/productsprocessing/edit_inline/tabular.html"

    fields = ('product', 'quantity_change', 'custom_price', 'total_cost', 'currency')
    readonly_fields = ('total_cost', 'currency')


class ProductProcessingNodeInlineCreateAdmin(ProductProcessingNodeInlineAdmin):
    extra = 1


class ProductProcessingNodeInlineChangeAdmin(ProductProcessingNodeInlineAdmin):
    extra = 0

    def get_readonly_fields(self, request, instance=None):
        if instance is not None and instance.closed:
            self.readonly_fields = ('product', 'quantity_change', 'custom_price', 'total_cost', 'currency')
            self.max_num = 0
            self.can_delete = False

        return super(ProductProcessingNodeInlineChangeAdmin, self).get_readonly_fields(request, instance)


class ProductProcessingResource(resources.ModelResource):

    class Meta:
        model = ProductsProcessing


@admin.register(ProductsProcessing)
class ProductsProcessingAdmin(ExportMixin, ModedInlinesMixin, admin.ModelAdmin):
    resource_class = ProductProcessingResource

    list_display = ('closed', 'type', 'name', 'created', 'total_cost_amount')
    list_display_links = ('name',)
    exclude = ('closed', 'deleted')
    search_fields = ('name', 'nodes__product__name')
    list_filter = ('type', 'created', 'closed')

    create_only_inlines = (ProductProcessingNodeInlineCreateAdmin,)
    change_only_inlines = (ProductProcessingNodeInlineChangeAdmin,)

    def get_readonly_fields(self, request, instance=None):
        if instance is not None and instance.closed:
            self.readonly_fields = ('type', 'description', 'name')
        else:
            self.readonly_fields = ()

        return super(ProductsProcessingAdmin, self).get_readonly_fields(request, instance)