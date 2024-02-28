from django.contrib import admin
from .models import Product, Supplier ,Inventory

admin.site.register(Product)
admin.site.register(Supplier)
admin.site.register(Inventory)