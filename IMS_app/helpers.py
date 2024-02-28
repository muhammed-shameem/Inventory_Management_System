from django.contrib.auth.models import User
from .models import Supplier

def create_user(username, password, is_superuser=False):
        user = User.objects.create_user(username, username + '@example.com', password)
        user.is_superuser = is_superuser
        user.save()
        return user

def create_supplier(username,phone_number):
    user = User.objects.create_user(username=username, password='supplierpass')
    return Supplier.objects.create(user=user, phone_number=phone_number, address='123 Main St')