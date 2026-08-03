from rest_framework import serializers

from .models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name")


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id", "first_name", "last_name", "full_name", "email", "phone",
            "department", "department_name", "position", "salary", "hire_date",
            "status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
