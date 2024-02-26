from django.core.exceptions import PermissionDenied
from .models import Supplier


class AdminLoginMixin:
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
        
        
class SupplierLoginMixin:
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        supplier = Supplier.objects.filter(user=user).first()
        if user.is_authenticated and supplier:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
