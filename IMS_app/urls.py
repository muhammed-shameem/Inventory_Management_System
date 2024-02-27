from django.urls import path

from . import views

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing_page'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('ims/dashboard', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('ims/products', views.AdminDashboardProductsView.as_view(), name='admin_dashboard_products'),
    path('ims/suppliers', views.AdminDashboardSuppliersView.as_view(), name='admin_dashboard_suppliers'),
    path('ims/supplier/<int:supplier_id>', views.AdminDashboardSupplierDetailView.as_view(), name='admin_supplier_detail'),
    path('ims/purchase/<int:product_id>', views.ProductPurchaseView.as_view(), name='purchase_product'),
    path('ims/reports', views.InventoryReportView.as_view(), name='inventory_report'),
    path('ims/reports/export/', views.export_csv, name='export_inventory_report'),
    path('supplier/dashboard', views.SupplierDashboardView.as_view(), name='supplier_dashboard'),
]