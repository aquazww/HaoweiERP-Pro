from django.urls import path
from .views import PurchaseReportView, SaleReportView, InventoryReportView, DashboardView, FinanceReportView

urlpatterns = [
    path('purchase/', PurchaseReportView.as_view(), name='purchase-report'),
    path('sale/', SaleReportView.as_view(), name='sale-report'),
    path('inventory/', InventoryReportView.as_view(), name='inventory-report'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('finance/', FinanceReportView.as_view(), name='finance-report'),
]
