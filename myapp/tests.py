from django.test import TestCase,Client
from .models import Product  # Correct the import path
from django.contrib.auth.models import User
from django.urls import reverse


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


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "kelvin"
        self.password = 'nnnn4444'
        self.user = User.objects.create_user(username= self.username,password=self.password)
    def test_login_success(self):
        response = self.client.post(reverse('login'),{
            'username':self.username,
            'password':self.password
        })
    def test_faliure_success(self):
        response = self.client.post(reverse('login'),{
            'username':self.username,
            'password':'wrong password'
        })         