from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return f"{self.id} - {self.user.username}"
    
    
class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} (Inventory)"