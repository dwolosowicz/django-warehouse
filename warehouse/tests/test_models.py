from warehouse.models import ProductProcessingNode, Product, Unit, Warehouse, Currency, ProductsProcessing
from django.test import TestCase
from decimal import *


def create_product_processing_node(product, product_processing, quantity_change):
    ppn = ProductProcessingNode(product=product, quantity_change=quantity_change, processing=product_processing)
    ppn.save()


def create_product_processing(product_quantity, quantity_change, processing_type):
    u = Unit(name="test_unit", slug="tu")
    u.save()

    c = Currency(name="Euro", slug="EUR")
    c.save()

    p = Product(name="Test_product", quantity=product_quantity, price="12.00", unit=u, currency=c)
    p.save()

    pp = ProductsProcessing(name="test", description="test", type=processing_type)
    pp.save()

    create_product_processing_node(p, pp, quantity_change)

    return p, pp


class ProductTestCase(TestCase):
    def test_reservation(self):
        """
        Tests whether the number of reserved units of product is properly calculated
        :return:
        """
        product, products_processing = create_product_processing(0, 10, ProductsProcessing.PROCESSING_RELEASE)
        _, products_processing_two = create_product_processing(0, 10, ProductsProcessing.PROCESSING_RELEASE)

        create_product_processing_node(product, products_processing_two, 15)

        self.assertEqual(25, product.reservation())


class ProductProcessingOperationsTestCase(TestCase):
    def test_total_cost_always_returns_decimal_without_custom_price(self):
        """
        Tests whether total_cost method always returns Decimal object as a return value
        """
        p = Product(price='0.00')
        ppn = ProductProcessingNode(product=p, quantity_change='1.00')

        self.assertIsInstance(ppn.total_cost(), Decimal)
        self.assertEqual(ppn.total_cost(), 0)

    def test_total_cost_always_returns_decimal_with_custom_price(self):
        """
        Tests whether total_cost method always returns Decimal object as a return value
        """
        p = Product()
        ppn = ProductProcessingNode(product=p, custom_price='0.00')

        self.assertIsInstance(ppn.total_cost(), Decimal)
        self.assertEqual(ppn.total_cost(), 0)

    def test_products_quantity_is_incremented(self):
        """
        Tests whether the quantity of products assigned to processing operations is incremented properly
        :return:
        """

        p, pp = create_product_processing(0, 10, ProductsProcessing.PROCESSING_ADMISSION)

        pp.close()

        self.assertEqual(10, Product.objects.get(pk=p.id).quantity)
        self.assertTrue(pp.closed)

    def test_products_quantity_is_decremented(self):
        """

        Tests whether the quantity of products assigned to processing operations is decremented properly
        :return:
        """

        p, pp = create_product_processing(10, 10, ProductsProcessing.PROCESSING_RELEASE)

        pp.close()

        self.assertTrue(0 == Product.objects.get(pk=p.id).quantity)
        self.assertTrue(pp.closed)