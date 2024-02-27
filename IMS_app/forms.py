from django import forms

class InventorySearchForm(forms.Form):
    product_name = forms.CharField(required=False)
    supplier_name = forms.CharField(required=False)
    quantity_min = forms.IntegerField(required=False)
    quantity_max = forms.IntegerField(required=False)