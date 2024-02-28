from django.core.exceptions import PermissionDenied
from .models import Supplier


class AdminLoginMixin:
    """
    Mixin for views that require an authenticated superuser (admin) to access.
    If the user is not authenticated or is not a superuser, a PermissionDenied exception is raised.
    """
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
        
        
class SupplierLoginMixin:
    """
    Mixin for views that require an authenticated user associated with a supplier to access.
    If the user is not authenticated or is not associated with a supplier, a PermissionDenied exception is raised.
    """
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        supplier = Supplier.objects.filter(user=user).first()
        if user.is_authenticated and supplier:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
