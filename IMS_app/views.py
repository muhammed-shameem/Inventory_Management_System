import csv
from django.db import transaction
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import UpdateView,DeleteView
from django.views.generic import TemplateView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Inventory, Product, Supplier
from .mixins import AdminLoginMixin, SupplierLoginMixin
from .forms import InventorySearchForm, ProductForm ,EditProductForm


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


class AdminDashboardView(AdminLoginMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_list = Inventory.objects.all()
        context['inventory_list'] = inventory_list
        return context


class AdminDashboardProductsView(AdminLoginMixin, TemplateView):
    template_name = 'admin/admin_product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.all()
        context['product_list'] = product_list
        return context


class AdminDashboardSuppliersView(AdminLoginMixin, TemplateView):
    template_name = 'admin/admin_suppliers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suppliers_list = Supplier.objects.all()
        context['suppliers_list'] = suppliers_list
        return context


class ProductPurchaseView(AdminLoginMixin, View):
    template_name = 'admin/purchase_product.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        return render(request, self.template_name, {'product': product})

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        intake_stock = request.POST.get('stock')
        if intake_stock:
            intake_stock = int(intake_stock)
            if not product.active_status:
                return render(request, self.template_name, {
                    'product': product,
                    'error': "The Product is not available"
                })
            if product.stock < intake_stock:
                return render(request, self.template_name, {
                    'product': product,
                    'error': "Not enough stock available"
                })

            with transaction.atomic():
                product.stock -= intake_stock
                if product.stock == 0:
                    product.active_status = False
                product.save()
                inventory_entry = Inventory.objects.filter(
                    product=product).first()
                if inventory_entry:
                    inventory_entry.stock += intake_stock
                    inventory_entry.save()
                else:
                    markup_percentage = 30
                    selling_unit_price_default = (int(
                        product.unit_price)) * (1 + markup_percentage / 100)
                    Inventory.objects.create(
                        product=product,
                        stock=intake_stock,
                        selling_unit_price=selling_unit_price_default)

            return redirect('admin_dashboard')

        return render(request, self.template_name, {
            'product': product,
            'error': "Stock missing in form"
        })


class AdminDashboardSupplierDetailView(AdminLoginMixin, TemplateView):
    template_name = 'admin/admin_supplier_detail.html'

    def get(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        products = Product.objects.filter(supplier=supplier)
        return render(request, self.template_name, {
            'supplier': supplier,
            'products': products
        })


class InventoryReportView(AdminLoginMixin, TemplateView):
    template_name = 'admin/admin_inventory_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = InventorySearchForm(self.request.GET)
        if form.is_valid():
            product_name = form.cleaned_data.get('product_name')
            supplier_name = form.cleaned_data.get('supplier_name')
            quantity_min = form.cleaned_data.get('quantity_min')
            quantity_max = form.cleaned_data.get('quantity_max')

            queryset = Inventory.objects.all()

            if product_name:
                queryset = queryset.filter(
                    product__name__icontains=product_name)
            if supplier_name:
                queryset = queryset.filter(
                    product__supplier__name__icontains=supplier_name)
            if quantity_min:
                queryset = queryset.filter(stock_quantity__gte=quantity_min)
            if quantity_max:
                queryset = queryset.filter(stock_quantity__lte=quantity_max)

            sort_by = self.request.GET.get('sort_by')
            if sort_by:
                queryset = queryset.order_by(sort_by)

            context['inventory'] = queryset

        context['form'] = form
        return context


class SupplierDashboardView(SupplierLoginMixin, TemplateView):
    template_name = 'supplier/supplier_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.request.user.supplier
        products = Product.objects.filter(supplier=supplier)
        context['products_list'] = products
        return context


class AddProductView(SupplierLoginMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'supplier/add_product.html'

    def form_valid(self, form):
        if hasattr(self.request.user, 'supplier'):
            supplier = self.request.user.supplier
            form.instance.supplier = supplier
            return super().form_valid(form)
        else:
            return HttpResponseForbidden(
                "You are not authorized to add products.")

    def get_success_url(self):
        return reverse_lazy('supplier_dashboard')
    
class EditProductView(SupplierLoginMixin, UpdateView):
    model = Product
    form_class = EditProductForm
    template_name = 'supplier/edit_product.html'
    success_url = reverse_lazy('supplier_dashboard')

    def form_valid(self, form):
        if form.instance.supplier.user != self.request.user:
            return HttpResponseForbidden("You are not authorized to edit this product.")
        return super().form_valid(form)
    
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'supplier/edit_product.html' 
    success_url = reverse_lazy('supplier_dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response_data = {'result': 'success', 'message': 'Product deleted successfully.'}
        return JsonResponse(response_data)


def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="inventory_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Product Name', 'Supplier', 'Purchase Price', 'Selling Price',
        'Quantity'
    ])

    queryset = Inventory.objects.all()
    for inventory in queryset:
        writer.writerow([
            inventory.product.name, inventory.product.supplier.user.username,
            inventory.product.unit_price, inventory.selling_unit_price,
            inventory.stock
        ])  # Adjust fields as needed

    return response
