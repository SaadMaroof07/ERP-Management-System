from rest_framework import serializers

from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "sku", "category", "category_name", "description", "unit",
            "cost_price", "unit_price", "quantity_in_stock", "reorder_level",
            "is_low_stock", "is_active", "created_at", "updated_at",
        )
        read_only_fields = ("id", "quantity_in_stock", "created_at", "updated_at")
        # quantity_in_stock is deliberately read-only here: it must only ever
        # change through a StockMovement (see StockMovementCreateSerializer)
        # or a Sale, never via a direct PATCH, so the ledger stays authoritative.


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = StockMovement
        fields = (
            "id", "product", "product_name", "movement_type", "quantity",
            "reference", "notes", "created_by_username", "created_at",
        )
        read_only_fields = ("id", "created_at")


class StockMovementCreateSerializer(serializers.Serializer):
    """Input serializer for POST /api/stock-movements/ - validates quantity
    sign against movement_type so a client can't sneak a negative quantity
    into an 'in' movement or vice versa."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    movement_type = serializers.ChoiceField(choices=StockMovement.MovementType.choices)
    quantity = serializers.IntegerField()
    notes = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["movement_type"] == StockMovement.MovementType.IN and attrs["quantity"] <= 0:
            raise serializers.ValidationError({"quantity": "Stock-in quantity must be positive."})
        if attrs["movement_type"] in (StockMovement.MovementType.OUT,) and attrs["quantity"] <= 0:
            raise serializers.ValidationError({"quantity": "Stock-out quantity must be entered as a positive number; it will be subtracted automatically."})
        return attrs
