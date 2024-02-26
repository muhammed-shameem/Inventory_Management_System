from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
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
                        
class AdminDashboardView(AdminLoginMixin,TemplateView):
    template_name = 'admin_dashboard.html'
    
class SupplierDashboardView(SupplierLoginMixin,TemplateView):
    template_name = 'supplier_dashboard.html'