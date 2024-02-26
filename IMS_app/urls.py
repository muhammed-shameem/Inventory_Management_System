from django.urls import path

from . import views

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing_page'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('ims/dashboard', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('supplier/dashboard', views.SupplierDashboardView.as_view(), name='supplier_dashboard'),
]