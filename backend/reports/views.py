from django.db.models import Count, F, Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import ReportsAndLogsPermission
from employees.models import Employee
from inventory.models import Product
from sales.models import Sale, SaleItem


class DashboardReportView(APIView):
    """GET /api/reports/dashboard/ - top-level KPIs for the admin/manager landing screen."""

    permission_classes = [ReportsAndLogsPermission]

    def get(self, request):
        total_employees = Employee.objects.filter(status=Employee.Status.ACTIVE).count()
        total_products = Product.objects.filter(is_active=True).count()
        low_stock_count = Product.objects.filter(is_active=True, quantity_in_stock__lte=F("reorder_level")).count()
        sales_qs = Sale.objects.filter(status=Sale.Status.COMPLETED)
        total_sales_amount = sales_qs.aggregate(total=Sum("total_amount"))["total"] or 0
        total_sales_count = sales_qs.count()
        inventory_value = Product.objects.filter(is_active=True).aggregate(
            value=Sum(F("unit_price") * F("quantity_in_stock"))
        )["value"] or 0

        return Response({
            "total_employees": total_employees,
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "total_sales_amount": total_sales_amount,
            "total_sales_count": total_sales_count,
            "inventory_value": inventory_value,
        })


class SalesReportView(APIView):
    """GET /api/reports/sales/ - top-selling products and recent sales."""

    permission_classes = [ReportsAndLogsPermission]

    def get(self, request):
        top_products = (
            SaleItem.objects.filter(sale__status=Sale.Status.COMPLETED)
            .values("product_name")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum(F("unit_price") * F("quantity")))
            .order_by("-total_quantity")[:10]
        )
        recent_sales = (
            Sale.objects.select_related("customer").order_by("-created_at")[:10]
            .values("id", "customer__name", "status", "total_amount", "created_at")
        )
        return Response({
            "top_products": list(top_products),
            "recent_sales": list(recent_sales),
        })


class InventoryReportView(APIView):
    """GET /api/reports/inventory/ - low-stock alert list + value by category."""

    permission_classes = [ReportsAndLogsPermission]

    def get(self, request):
        low_stock = (
            Product.objects.filter(is_active=True, quantity_in_stock__lte=F("reorder_level"))
            .values("id", "name", "sku", "quantity_in_stock", "reorder_level")
            .order_by("quantity_in_stock")
        )
        by_category = (
            Product.objects.filter(is_active=True)
            .values("category__name")
            .annotate(product_count=Count("id"), total_units=Sum("quantity_in_stock"))
            .order_by("-total_units")
        )
        return Response({
            "low_stock_products": list(low_stock),
            "by_category": list(by_category),
        })


class EmployeeReportView(APIView):
    """GET /api/reports/employees/ - headcount by department and status."""

    permission_classes = [ReportsAndLogsPermission]

    def get(self, request):
        by_department = (
            Employee.objects.values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        by_status = Employee.objects.values("status").annotate(count=Count("id")).order_by("-count")
        return Response({
            "by_department": list(by_department),
            "by_status": list(by_status),
        })
