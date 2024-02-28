from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    """
    Represents a supplier in the system.

    Attributes:
        user (User): The user associated with the supplier.
        phone_number (str): The phone number of the supplier.
        address (str): The address of the supplier.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20,unique=True)
    address = models.TextField()

    def __str__(self):
        return f"{self.id} - {self.user.username}"
    
    
class Product(models.Model):
    """
    Represents a product offered by a supplier.

    Attributes:
        supplier (Supplier): The supplier associated with the product.
        name (str): The name of the product.
        description (str): The description of the product.
        unit_price (Decimal): The unit price of the product.
        stock (int): The current stock quantity of the product.
        active_status (bool): Indicates if the product is active or not.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.PositiveIntegerField()
    active_status=models.BooleanField(default=True)

    def __str__(self):
        return self.name
    


class Inventory(models.Model):
    """
    Represents the inventory of a product.

    Attributes:
        product (Product): The product associated with the inventory.
        selling_unit_price (Decimal): The selling unit price of the product in the inventory.
        stock (int): The current stock quantity of the product in the inventory.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (Inventory)"