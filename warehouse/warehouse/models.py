from decimal import Context, Decimal

from django.db import models
from safedelete import safedelete_mixin_factory, SOFT_DELETE
from django_extensions.db import fields


class Currency(models.Model):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=6)

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def __str__(self):
        return "{} ({})".format(self.slug, self.name)


class Warehouse(models.Model):
    name = models.CharField(max_length=255)

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def products_count(self):
        return self.product_set.count()

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=6)

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def __str__(self):
        return "{} ({})".format(self.slug, self.name)


SafeDeleteMixin = safedelete_mixin_factory(SOFT_DELETE)


class Product(SafeDeleteMixin):
    warehouses = models.ManyToManyField(Warehouse)

    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default='0.00')

    price = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
    currency = models.ForeignKey(Currency, on_delete=models.DO_NOTHING)

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def amount(self):
        return "{} {}".format(self.quantity, self.unit.slug)

    def cost(self):
        return "{} {}".format(self.price, self.currency.slug)

    def reservation_amount(self):
        return "{} {}".format(self.reservation(), self.unit.slug)

    def reservation(self):
        nodes = self.nodes.filter(processing__type=ProductsProcessing.PROCESSING_RELEASE, processing__closed=False)
        quantity_changes = [product_processing_node.quantity_change for product_processing_node in nodes]

        return sum(quantity_changes)

    def __str__(self):
        return self.name


class ProductsProcessing(SafeDeleteMixin):
    PROCESSING_RELEASE = 'RS'
    PROCESSING_ADMISSION = 'AN'

    PROCESSING_TYPES = (
        ('', 'Choose the type'),
        (PROCESSING_RELEASE, 'Release'),
        (PROCESSING_ADMISSION, 'Admission'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(choices=PROCESSING_TYPES, max_length=2)

    closed = models.BooleanField(default=False, verbose_name="Status")

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def __str__(self):
        return self.name

    def total_cost_amount(self):
        if self.nodes.all().count() > 0:
            return "{} {}".format(self.total_cost(), self.nodes.all()[0].currency())
        else:
            return "(None)"

    total_cost_amount.short_description = "Total"

    def total_cost(self):
        return sum([ppn.total_cost() for ppn in self.nodes.all()])

    def is_release(self):
        return self.type == self.PROCESSING_RELEASE

    def is_admission(self):
        return self.type == self.PROCESSING_ADMISSION

    def clean_for_processing(self):
        if self.closed:
            return False

        for product_node in self.nodes.all():
            if not product_node.clean_for_processing():
                return False

        return True

    def close(self):
        self.closed = True

        self._perform_nodes_operation(self.type)

    def _perform_nodes_operation(self, processing_type):
        for product_node in self.nodes.all():
            if processing_type == self.PROCESSING_ADMISSION:
                product_node.perform_admission()
            else:
                product_node.perform_release()


class ProductProcessingNode(models.Model):
    class Meta:
        unique_together = ('product', 'processing')

    processing = models.ForeignKey(ProductsProcessing, related_name="nodes")
    product = models.ForeignKey(Product, related_name="nodes")

    quantity_change = models.DecimalField(max_digits=10, decimal_places=3, default='0.000')
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def is_admitted(self):
        return self.processing.is_admission()

    def is_released(self):
        return self.processing.is_release()

    def total_cost(self):
        return Context().multiply(Decimal(self.quantity_change), Decimal(self.custom_price or self.product.price))

    def currency(self):
        return self.product.currency.slug

    def clean_for_processing(self):
        if self.is_released():
            return self.product.quantity - self.quantity_change >= 0
        else:
            return True

    def is_closable(self):
        return self.clean_for_processing() and not self.processing.closed

    def perform_admission(self):
        self.product.quantity = Decimal(self.product.quantity) + Decimal(self.quantity_change)
        self.product.save()

    def perform_release(self):
        self.product.quantity = Decimal(self.product.quantity) - Decimal(self.quantity_change)
        self.product.save()