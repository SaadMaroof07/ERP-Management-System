from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from accounts.models import ActivityLog, log_activity
from accounts.permissions import IsAdminOrManager

from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrManager]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department", "created_by").all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrManager]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "status"]
    search_fields = ["first_name", "last_name", "email", "position"]
    ordering_fields = ["hire_date", "salary", "created_at", "last_name"]

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_activity(self.request, ActivityLog.Action.CREATE, "employees", obj, "Employee record created")

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request, ActivityLog.Action.UPDATE, "employees", obj, "Employee record updated")

    def perform_destroy(self, instance):
        log_activity(self.request, ActivityLog.Action.DELETE, "employees", instance, "Employee record deleted")
        instance.delete()
