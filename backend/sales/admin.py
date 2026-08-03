from django.contrib import admin

from .models import Customer, Sale, SaleItem

admin.site.register(Customer)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_amount", "created_at")
    list_filter = ("status",)
    inlines = [SaleItemInline]
