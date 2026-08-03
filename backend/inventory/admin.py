from django.contrib import admin

from .models import Category, Product, StockMovement

admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "quantity_in_stock", "reorder_level", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "product", "movement_type", "quantity", "created_by")
    list_filter = ("movement_type",)
