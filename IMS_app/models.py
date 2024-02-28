from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

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
    
    def clean(self):
        if self.phone_number and len(self.phone_number)>20:
            raise ValidationError({'phone_number': ['Phone number length must be less than or equal to 20.']})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.user.username}"
    
    
class Product(models.Model):
    """
    Represents a product offered by a supplier.

    Attributes:
        supplier (Supplier): The supplier associated with the product.
        name (str): The name of the product. (Required field; cannot be blank or null.)
        description (str): The description of the product.
        unit_price (Decimal): The unit price of the product. Must be greater than or equal to 0.01.
        stock (int): The current stock quantity of the product.
        active_status (bool): Indicates if the product is active or not.

    Note:
        - The `unit_price` field enforces a minimum value constraint of 0.01.
        - The `name` field is a required field and cannot be blank or null. If not provided,
            a `ValidationError` will be raised during the `clean` method.
        - The `clean` method additionally checks for negative values in the `unit_price` field.
        - In SQLite, if a text field is defined as not null and a constraint is not met (e.g., an empty string),
            the `clean` method raises a `ValidationError` to ensure data integrity.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.PositiveIntegerField()
    active_status=models.BooleanField(default=True)
    
    def clean(self):
        if self.unit_price < Decimal('0.01'):
            raise ValidationError({'unit_price': ['Unit price must be greater than or equal to 0.01.']})
        
        if not self.name:
            raise ValidationError({'name': ['This is a required field']})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    selling_unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (Inventory)"