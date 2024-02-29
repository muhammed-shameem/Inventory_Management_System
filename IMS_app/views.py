import csv
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import TemplateView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse,HttpResponseForbidden
from .models import Inventory, Product, Supplier
from .mixins import AdminLoginMixin, SupplierLoginMixin
from .forms import InventorySearchForm, ProductForm, EditProductForm


class LandingView(TemplateView):
    """
    View for rendering the landing page.
    """
    template_name = 'landing_page.html'


class CustomLoginView(LoginView):
    """
    Customized login view that redirects users based on their role after successful login.

    Attributes:
    - template_name: The HTML template for rendering the login page.

    Methods:
    - get_success_url: Overrides the default behavior to redirect users to different dashboards based on their role(admin or supplier).

    Usage:
    - Extends Django's built-in LoginView.
    """
    
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return reverse_lazy('admin_dashboard')
        else:
            return reverse_lazy('supplier_dashboard')


class CustomLogoutView(LogoutView):
    """
    Customized logout view that redirects users to the login page after successful logout.

    Attributes:
    - next_page: URL to redirect the user to after successful logout.

    Usage:
    - Extends Django's built-in LogoutView.
    """
    next_page = reverse_lazy('login')


class AdminDashboardView(AdminLoginMixin, TemplateView):
    """
    Admin dashboard view displaying the inventory list with search functionality.

    Attributes:
    - template_name: The HTML template for rendering the admin dashboard.

    Methods:
    - get_context_data: Overrides the method to include the inventory list and search query in the context.

    Usage:
    - Extends Django's TemplateView and uses the AdminLoginMixin for permission checks.
    """
    
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_list = Inventory.objects.all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            inventory_list = inventory_list.filter(
                Q(product__name__icontains=search_query)
                | Q(product__description__icontains=search_query))

        context['inventory_list'] = inventory_list
        context['search_query'] = search_query
        return context


class AdminDashboardProductsView(AdminLoginMixin, TemplateView):
    """
    Admin dashboard view displaying a list of products with search functionality.

    Attributes:
    - template_name: The HTML template for rendering the admin product list.

    Methods:
    - get_context_data: Overrides the method to include the product list and search query in the context.

    Usage:
    - Extends Django's TemplateView and uses the AdminLoginMixin for permission checks.
    """
    
    template_name = 'admin/admin_product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.all()

        search_query = self.request.GET.get('search', '')
        if search_query:
            product_list = product_list.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(supplier__user__username__icontains=search_query))

        context['product_list'] = product_list
        context['search_query'] = search_query
        return context


class AdminDashboardSuppliersView(AdminLoginMixin, TemplateView):
    """
    Admin dashboard view displaying a list of suppliers with search functionality.

    Attributes:
    - template_name: The HTML template for rendering the admin suppliers list.

    Methods:
    - get_context_data: Overrides the method to include the suppliers list and search query in the context.

    Usage:
    - Extends Django's TemplateView and uses the AdminLoginMixin for permission checks.
    """
    
    template_name = 'admin/admin_suppliers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        suppliers_list = Supplier.objects.all()
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            suppliers_list = suppliers_list.filter(
                Q(user__username__icontains=search_query)
                | Q(user__first_name__icontains=search_query))
            
        context['suppliers_list'] = suppliers_list
        context['search_query'] = search_query
        return context


class ProductPurchaseView(AdminLoginMixin, View):
    """
    Admin view for purchasing a product and updating inventory.

    Attributes:
    - template_name: The HTML template for rendering the product purchase page.

    Methods:
    - get: Handles GET requests to display the product information.
    - post: Handles POST requests to process the product purchase and update inventory.

    Usage:
    - Extends Django's View and uses the AdminLoginMixin for permission checks.
    """
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
    """
    Admin dashboard view displaying details of a specific supplier and their associated products.

    Attributes:
    - template_name: The HTML template for rendering the admin supplier detail page.

    Methods:
    - get: Handles the HTTP GET request to retrieve and display details of the specified supplier.

    Parameters:
    - request: The HTTP request object.
    - supplier_id: The ID of the supplier to retrieve details for.

    Returns:
    - HttpResponse: Rendered HTML page with supplier details and associated products.

    Usage:
    - Extends Django's TemplateView and uses the AdminLoginMixin for permission checks.
    """
    
    template_name = 'admin/admin_supplier_detail.html'

    def get(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id)
        products = Product.objects.filter(supplier=supplier)
        return render(request, self.template_name, {
            'supplier': supplier,
            'products': products
        })


class InventoryReportView(AdminLoginMixin, TemplateView):
    """
    Admin dashboard view generating an inventory report with search and sorting functionality.

    Attributes:
    - template_name: The HTML template for rendering the admin inventory report.

    Methods:
    - get_context_data: Overrides the method to include the inventory report and search form in the context.

    Usage:
    - Extends Django's TemplateView and uses the AdminLoginMixin for permission checks.
    """
    
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
                
            search_query = self.request.GET.get('search', '')
            if search_query:
                queryset = queryset.filter(
                    Q(product__name__icontains=search_query)
                    | Q(product__description__icontains=search_query)
                    | Q(product__supplier__user__username=search_query)
                    )
                
            context['search_query'] = search_query

            context['inventory'] = queryset

        context['form'] = form
        return context


class SupplierDashboardView(SupplierLoginMixin, TemplateView):
    """
    Supplier dashboard view displaying a list of products with search functionality.

    Attributes:
    - template_name: The HTML template for rendering the supplier dashboard.

    Methods:
    - get_context_data: Overrides the method to include the products list and search query in the context.

    Usage:
    - Extends Django's TemplateView and uses the SupplierLoginMixin for permission checks.
    """
    
    template_name = 'supplier/supplier_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.request.user.supplier
        products = Product.objects.filter(supplier=supplier)
        search_query = self.request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query))
        context['products_list'] = products
        context['search_query'] = search_query
        return context


class AddProductView(SupplierLoginMixin, CreateView):
    """
    View for adding a new product to the supplier's inventory(Product Table).

    Attributes:
    - model: The model to use for creating the new product (Product).
    - form_class: The form class to use for creating the new product (ProductForm).
    - template_name: The HTML template for rendering the add product page.

    Methods:
    - form_valid: Overrides the method to associate the product with the logged-in supplier.
    - get_success_url: Returns the URL to redirect to after successfully adding the product.

    Usage:
    - Extends Django's CreateView and uses the SupplierLoginMixin for permission checks.
    """
    
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
    """
    View for editing an existing product in the supplier's inventory.

    Attributes:
    - model: The model to use for updating the product (Product).
    - form_class: The form class to use for updating the product (EditProductForm).
    - template_name: The HTML template for rendering the edit product page.
    - success_url: The URL to redirect to after successfully updating the product (supplier_dashboard).

    Methods:
    - form_valid: Overrides the method to check if the logged-in supplier is authorized to edit the product.

    Usage:
    - Extends Django's UpdateView and uses the SupplierLoginMixin for permission checks.
    """
    
    model = Product
    form_class = EditProductForm
    template_name = 'supplier/edit_product.html'
    success_url = reverse_lazy('supplier_dashboard')

    def form_valid(self, form):
        if form.instance.supplier.user != self.request.user:
            return HttpResponseForbidden(
                "You are not authorized to edit this product.")
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    """
    View for deleting an existing product from the supplier's inventory.

    Attributes:
    - model: The model to use for deleting the product (Product).
    - template_name: The HTML template for rendering the delete product confirmation page.
    - success_url: The URL to redirect to after successfully deleting the product (supplier_dashboard).

    Methods:
    - delete: Overrides the method to handle the deletion of the product and return a JsonResponse.

    Usage:
    - Extends Django's DeleteView.
    """
    
    model = Product
    template_name = 'supplier/edit_product.html'
    success_url = reverse_lazy('supplier_dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response_data = {
            'result': 'success',
            'message': 'Product deleted successfully.'
        }
        return JsonResponse(response_data)

