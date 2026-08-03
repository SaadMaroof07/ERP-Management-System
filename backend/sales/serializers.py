from rest_framework import serializers

from inventory.models import Product

from .models import Customer, Sale, SaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "address", "created_at")


class SaleItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = SaleItem
        fields = ("id", "product", "product_name", "unit_price", "quantity", "subtotal")
        read_only_fields = ("id", "product_name", "unit_price")


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True, default=None)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Sale
        fields = (
            "id", "customer", "customer_name", "status", "total_amount",
            "notes", "items", "created_by_username", "created_at",
        )
        read_only_fields = ("id", "total_amount", "created_at")


class SaleItemInputSerializer(serializers.Serializer):
    """Only product + quantity come from the client. Price is always
    looked up from the live Product record server-side during checkout -
    the client can never supply or influence a price, exactly like the
    Week 02 e-commerce checkout."""

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class SaleCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False, allow_null=True)
    notes = serializers.CharField(max_length=255, required=False, allow_blank=True)
    items = SaleItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("A sale must include at least one item.")
        return value
