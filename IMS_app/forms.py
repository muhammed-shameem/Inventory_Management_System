from django import forms
from .models import Product

class InventorySearchForm(forms.Form):
    product_name = forms.CharField(required=False)
    supplier_name = forms.CharField(required=False)
    quantity_min = forms.IntegerField(required=False)
    quantity_max = forms.IntegerField(required=False)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price', 'stock']