from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Supplier,Product

USERNAME = "Test Supplier"
PASSWORD = 'testpassword'
PHONE_NUMBER = "123-456-7890"
ADDRESS = "Test Address"
PRODUCT_NAME = "Test Supplier"
PRODUCT_DESC = "123-456-7890"
UNIT_PRICE = Decimal('12.34')
STOCK=50
ACTIVE_STATUS = True

class TestSupplierModel(TestCase):
    """
    Test cases for the Supplier model.

    - `test_instance`: Test the creation of a Supplier instance with valid data.
    - `test_unique_user_is_enforced`: Test that creating two suppliers with the same user raises an Exception.
    - `test_unique_phone_number`: Test that creating a supplier with an existing phone number raises an Exception.
    - `test_phone_number_length`: Test that creating a supplier with an invalid phone number length raises an Exception.
    """
    
    def setUp(self):
        self.user = User.objects.create(username=USERNAME, password=PASSWORD)
        self.supplier = Supplier.objects.create(
            user=self.user,
            phone_number=PHONE_NUMBER,
            address=ADDRESS
        )

    def test_instance(self):
        self.assertEqual(self.supplier.user, self.user)
        self.assertEqual(self.supplier.phone_number, PHONE_NUMBER)
        self.assertEqual(self.supplier.address, ADDRESS)

    def test_unique_user_is_enforced(self):
        with self.assertRaises(Exception):
            Supplier.objects.create(
                user=self.user,
                phone_number="987-654-3210",
                address="Another Address"
            )
    def test_unique_phone_number(self):
        different_user = User.objects.create(username='DifferentUser', password='password')
        with self.assertRaises(Exception):
            Supplier.objects.create(
                user=different_user,
                phone_number=PHONE_NUMBER,
                address="Address"
            )
    def test_phone_number_length(self):
        invalid_phone_number = "12345678901234567890123" 
        with self.assertRaises(Exception):
            Supplier.objects.create(
                user=self.user,
                phone_number=invalid_phone_number,
                address="Address"
            )
            
class TestProductModel(TestCase):
    """
    Test cases for the Product model.

    - `test_instance`: Test the creation of a Product instance with valid data.
    - `test_name_required`: Test that creating a product without a name raises an Exception.
    - `test_negative_unit_price`: Test that creating a product with a negative unit price raises an Exception.
    - `test_negative_stock_quantity`: Test that creating a product with a negative stock quantity raises an Exception.
    """

    def setUp(self):
        self.user = User.objects.create(username=USERNAME, password=PASSWORD)
        self.supplier = Supplier.objects.create(
            user=self.user,
            phone_number=PHONE_NUMBER,
            address=ADDRESS
        )

    def test_instance(self):
        product = Product.objects.create(
            supplier=self.supplier,
            name=PRODUCT_NAME,
            description=PRODUCT_DESC,
            unit_price=UNIT_PRICE,
            stock=STOCK,
            active_status=ACTIVE_STATUS
        )
        self.assertEqual(product.supplier, self.supplier)
        self.assertEqual(product.name, PRODUCT_NAME)
        self.assertEqual(product.description, PRODUCT_DESC)
        self.assertEqual(product.unit_price, UNIT_PRICE)
        self.assertEqual(product.stock, STOCK)
        self.assertTrue(product.active_status)

    def test_name_required(self):
        p=Product.objects.create(
                supplier=self.supplier,
                description=PRODUCT_DESC,
                unit_price=UNIT_PRICE,
                stock=STOCK,
                active_status=ACTIVE_STATUS
            )
        with self.assertRaises(ValidationError):
            Product.objects.create(
                supplier=self.supplier,
                description=PRODUCT_DESC,
                unit_price=UNIT_PRICE,
                stock=STOCK,
                active_status=ACTIVE_STATUS
            )

    def test_negative_unit_price(self):
        with self.assertRaises(Exception):
            Product.objects.create(
                supplier=self.supplier,
                name=PRODUCT_NAME,
                description=PRODUCT_DESC,
                unit_price=-5000000.123,
                stock=STOCK,
                active_status=ACTIVE_STATUS
            )

    def test_negative_stock_quantity(self):
        with self.assertRaises(Exception):
            Product.objects.create(
                supplier=self.supplier,
                name=PRODUCT_NAME,
                description=PRODUCT_DESC,
                unit_price=UNIT_PRICE,
                stock=-10,
                active_status=ACTIVE_STATUS
            )
