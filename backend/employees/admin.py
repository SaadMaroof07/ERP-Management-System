from django.contrib import admin

from .models import Department, Employee

admin.site.register(Department)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "department", "position", "status", "hire_date")
    list_filter = ("department", "status")
    search_fields = ("first_name", "last_name", "email")
