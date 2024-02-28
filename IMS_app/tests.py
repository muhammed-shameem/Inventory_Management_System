from django.test import TestCase,Client
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.urls import reverse,reverse_lazy
from .models import Supplier,Product,Inventory
from .helpers import create_user,create_supplier


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
        self.different_user = User.objects.create(username='DifferentUser', password='password')
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
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                user=self.user,
                phone_number="987-654-3210",
                address="Another Address"
            )
    def test_unique_phone_number(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                user=self.different_user,
                phone_number=PHONE_NUMBER,
                address="Address"
            )
    def test_phone_number_length(self):
        invalid_phone_number = "12345678901234567890123" 
        with self.assertRaises(ValidationError):
            Supplier.objects.create(
                user=self.different_user,
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
        with self.assertRaises(ValidationError):
            Product.objects.create(
                supplier=self.supplier,
                description=PRODUCT_DESC,
                unit_price=UNIT_PRICE,
                stock=STOCK,
                active_status=ACTIVE_STATUS
            )

    def test_negative_unit_price(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                supplier=self.supplier,
                name=PRODUCT_NAME,
                description=PRODUCT_DESC,
                unit_price=-5000000.123,
                stock=STOCK,
                active_status=ACTIVE_STATUS
            )

    def test_negative_stock_quantity(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                supplier=self.supplier,
                name=PRODUCT_NAME,
                description=PRODUCT_DESC,
                unit_price=UNIT_PRICE,
                stock=-10,
                active_status=ACTIVE_STATUS
            )
            
            
class TestInventoryModel(TestCase):
    """
    Test cases for the Inventory model.

    - `test_instance`: Test the creation of an Inventory instance with valid data.
    - `test_negative_selling_unit_price`: Test that creating an inventory with a negative selling unit price raises a ValidationError.
    - `test_negative_stock_quantity`: Test that creating an inventory with a negative stock quantity raises a ValidationError.
    - `test_unique_product`: Test that creating two inventories with the same product raises an IntegrityError.
    """

    def setUp(self):
        self.user = User.objects.create(username=USERNAME, password=PASSWORD)
        self.supplier = Supplier.objects.create(
            user=self.user,
            phone_number=PHONE_NUMBER,
            address=ADDRESS
        )
        self.product = Product.objects.create(
            supplier=self.supplier,
            name=PRODUCT_NAME,
            description=PRODUCT_DESC,
            unit_price=UNIT_PRICE,
            stock=STOCK,
            active_status=ACTIVE_STATUS
        )

    def test_instance(self):
        inventory = Inventory.objects.create(
            product=self.product,
            selling_unit_price=Decimal('15.00'),
            stock=30
        )
        self.assertEqual(inventory.product, self.product)
        self.assertEqual(inventory.selling_unit_price, Decimal('15.00'))
        self.assertEqual(inventory.stock, 30)

    def test_negative_selling_unit_price(self):
        with self.assertRaises(ValidationError):
            Inventory.objects.create(
                product=self.product,
                selling_unit_price=Decimal('-5.00'),
                stock=30
            )

    def test_negative_stock_quantity(self):
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                product=self.product,
                selling_unit_price=Decimal('15.00'),
                stock=-10
            )

    def test_unique_product(self):
        Inventory.objects.create(
            product=self.product,
            selling_unit_price=Decimal('15.00'),
            stock=30
        )
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                product=self.product,
                selling_unit_price=Decimal('20.00'),
                stock=15
            )

class CustomLoginViewTest(TestCase):
    """
    Test cases for the CustomLoginView.

    Methods:
    - setUp: Setup method to create test users for admin and supplier.

    Test Cases:
    - test_login_redirect_admin: Checks if the admin user is redirected to the admin dashboard.
    - test_login_redirect_supplier: Checks if the supplier user is redirected to the supplier dashboard.
    - test_login_invalid_credentials: Checks if login fails with invalid username or password.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        self.supplier = Supplier.objects.create(user=self.user, phone_number=PHONE_NUMBER,address=ADDRESS)
        self.admin = User.objects.create_superuser(
            username='admin', password='testpassword', email="admin@example.com")

    def test_login_redirect_admin(self):
        client = Client()
        response = client.post(reverse('login'), {'username': self.admin.username, 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302) #success status code
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_login_redirect_supplier(self):
        client = Client()
        response = client.post(reverse('login'), {'username': self.supplier.user.username, 'password': PASSWORD})
        self.assertEqual(response.status_code, 302)#success status code
        self.assertRedirects(response, reverse('supplier_dashboard'))
        
    def test_login_invalid_credentials(self):
        client = Client()
        response = client.post(reverse('login'), {'username': 'invaliduser', 'password': 'invalidpassword'})
        self.assertEqual(response.status_code, 200)#failure status code
        self.assertTemplateUsed(response, 'login.html')
        
        
class AdminDashboardViewTest(TestCase):
    
    """
    Test cases for the AdminDashboardView.

    Methods:
    - setUp: Setup method to create test admin user and products with inventory.
    - test_get_context_data_no_search: Checks if the context is correctly populated without search query.
    - test_get_context_data_with_search: Checks if the context is correctly filtered with a search query.
    - test_access_denied_for_non_admin: Checks if access is denied for non-admin users.
    - test_unauthorized_access: Checks if access is denied for non-logged users.
    """

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin', password='testpassword', email="admin@example.com")
        product1 = Product.objects.create(
            supplier=create_supplier('user1','1234567'),
            name="Product 1",
            description="Product description 1",
            unit_price=Decimal('10.00'),
            stock=10,
            active_status=True
        )
        Inventory.objects.create(product=product1, selling_unit_price=Decimal('12.00'), stock=5)

        product2 = Product.objects.create(
            supplier=create_supplier('user2','1234566787'),
            name="Product 2",
            description="Product description 2",
            unit_price=Decimal('20.00'),
            stock=20,
            active_status=True
        )
        Inventory.objects.create(product=product2, selling_unit_price=Decimal('25.00'), stock=15)

    def test_get_context_data_no_search(self):
        self.client.login(username='admin', password='testpassword')
        response = self.client.get(reverse_lazy('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['inventory_list']), 2)
        self.assertEqual(response.context['search_query'], '')
        self.client.logout()

    def test_get_context_data_with_search(self):
        self.client.login(username='admin', password='testpassword')
        search_query = 'Product 1'
        response = self.client.get(reverse_lazy('admin_dashboard'), {'search': search_query})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['inventory_list']), 1)
        self.assertEqual(response.context['inventory_list'][0].product.name, search_query)
        self.client.logout()
        
    def test_access_denied_for_non_admin(self):
        user = User.objects.create_user('supplieruser', 'password', 'user@example.com')
        self.client.login(username='supplieruser', password='password')
        response = self.client.get(reverse_lazy('admin_dashboard'))
        self.assertEqual(response.status_code, 403) 
        self.client.logout() 
    
    def test_unauthorized_access(self):
        response = self.client.get(reverse_lazy('admin_dashboard'))
        self.assertEqual(response.status_code, 403)  
        
        
        
class SupplierDashboardViewTest(TestCase):
    """
    Test cases for the SupplierDashboardView.

    Methods:
    - setUp: Setup method to create a test supplier user and products.
    - test_get_context_data_no_search: Checks if the context is correctly populated without a search query.
    - test_get_context_data_with_search: Checks if the context is correctly filtered with a search query.
    - test_access_denied_for_non_supplier: Checks if access is denied for non-supplier users.
    """

    def setUp(self):
        self.client = Client()
        self.supplier = create_supplier(username='supplieruser',phone_number="1233456787888")

        product1 = Product.objects.create(
            supplier=self.supplier,
            name="Product 1",
            description="Product description 1",
            unit_price=10.00,
            stock=10,
            active_status=True
        )

        product2 = Product.objects.create(
            supplier=self.supplier,
            name="Product 2",
            description="Product description 2",
            unit_price=20.00,
            stock=20,
            active_status=True
        )

    def test_get_context_data_no_search(self):
        self.client.login(username='supplieruser', password='supplierpass')
        response = self.client.get(reverse_lazy('supplier_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products_list']), 2)
        self.assertEqual(response.context['search_query'], '')
        self.client.logout()

    def test_get_context_data_with_search(self):
        self.client.login(username='supplieruser', password='supplierpass')
        search_query = 'Product 1'
        response = self.client.get(reverse_lazy('supplier_dashboard'), {'search': search_query})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products_list']), 1)
        self.assertEqual(response.context['products_list'][0].name, search_query)
        self.client.logout()
        
    def test_access_denied_for_non_supplier(self):
        user = create_user(username='normaluser', password='user@example.com')
        self.client.login(username='normaluser', password='user@example.com')
        response = self.client.get(reverse_lazy('supplier_dashboard'))
        self.assertEqual(response.status_code, 403) 
        self.client.logout() 
