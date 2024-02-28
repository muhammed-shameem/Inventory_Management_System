from django import forms
from .models import Product

class InventorySearchForm(forms.Form):
    """
    Form for searching products in the inventory.
    
    Fields:
    - product_name: Search by product name (optional).
    - supplier_name: Search by supplier name (optional).
    - quantity_min: Minimum quantity threshold (optional).
    - quantity_max: Maximum quantity threshold (optional).
    """
    product_name = forms.CharField(required=False)
    supplier_name = forms.CharField(required=False)
    quantity_min = forms.IntegerField(required=False)
    quantity_max = forms.IntegerField(required=False)

class ProductForm(forms.ModelForm):
    """
    Form for creating or updating a product in the inventory.

    Fields:
    - name: Product name.
    - description: Product description.
    - unit_price: Price per unit of the product.
    - stock: Current stock quantity.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price', 'stock']
        
class EditProductForm(forms.ModelForm):
    """
    Form for editing a product in the inventory, including the ability to change the active status.

    Fields:
    - name: Product name.
    - description: Product description.
    - unit_price: Price per unit of the product.
    - stock: Current stock quantity.
    - active_status: Checkbox to set the active status of the product.
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price', 'stock','active_status']
        widgets = {
            'active_status': forms.CheckboxInput(attrs={'class': 'active_status'}),
        }