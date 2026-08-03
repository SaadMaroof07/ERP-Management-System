from django.urls import path

from .views import DashboardReportView, EmployeeReportView, InventoryReportView, SalesReportView

urlpatterns = [
    path("reports/dashboard/", DashboardReportView.as_view(), name="report-dashboard"),
    path("reports/sales/", SalesReportView.as_view(), name="report-sales"),
    path("reports/inventory/", InventoryReportView.as_view(), name="report-inventory"),
    path("reports/employees/", EmployeeReportView.as_view(), name="report-employees"),
]
