from django.test import TestCase
from .models import Product  # Correct the import path


class ProductModelTest(TestCase):
    def test_product_creation(self):
        product = Product.objects.create(
            name="Test Product", 
            price=1000, 
            description="A sample test product"
        )
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.price, 1000)
        self.assertEqual(product.description, "A sample test product")
