from django.views.generic import TemplateView
from django.db import transaction
from django.contrib.auth.views import LoginView,LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from .models import Inventory,Product,Supplier
from .mixins import AdminLoginMixin,SupplierLoginMixin

class LandingView(TemplateView):
    template_name = 'landing_page.html'
    
class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return reverse_lazy('admin_dashboard')
        else:
            return reverse_lazy('supplier_dashboard')
        
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
                        
class AdminDashboardView(AdminLoginMixin,TemplateView):
    template_name = 'admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_list = Inventory.objects.all()
        context['inventory_list'] = inventory_list
        return context
    
class AdminDashboardProductsView(AdminLoginMixin,TemplateView):
    template_name = 'admin_product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.all()
        context['product_list'] = product_list
        return context
    
class AdminDashboardSuppliersView(AdminLoginMixin,TemplateView):
    template_name = 'admin_suppliers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suppliers_list = Supplier.objects.all()
        context['suppliers_list'] = suppliers_list
        return context
class ProductPurchaseView(AdminLoginMixin, View):
    template_name = 'purchase_product.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        return render(request, self.template_name, {'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        intake_stock=request.POST.get('stock')
        if intake_stock:
            intake_stock = int(intake_stock)
            if not product.active_status:
                return render(request, self.template_name, {'product': product, 'error': "The Product is not available"})
            if product.stock < intake_stock:
                return render(request, self.template_name, {'product': product, 'error': "Not enough stock available"})
            
            with transaction.atomic():
                product.stock -= intake_stock
                if product.stock == 0:
                    product.active_status = False
                product.save()
                inventory_entry = Inventory.objects.filter(product=product).first()
                if inventory_entry:
                    inventory_entry.stock += intake_stock
                    inventory_entry.save()
                else:
                    markup_percentage = 30
                    selling_unit_price_default = (int(product.unit_price)) * (1 + markup_percentage / 100)
                    Inventory.objects.create(product=product, stock=intake_stock,selling_unit_price=selling_unit_price_default)

            return redirect('admin_dashboard')

        return render(request, self.template_name, {'product': product, 'error': "Stock missing in form"})

    
class SupplierDashboardView(SupplierLoginMixin,TemplateView):
    template_name = 'supplier_dashboard.html'