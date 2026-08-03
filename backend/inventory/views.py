from django.db import transaction
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, viewsets
from rest_framework.response import Response

from accounts.models import ActivityLog, log_activity
from accounts.permissions import InventoryWritePermission

from .models import Category, Product, StockMovement
from .serializers import (
    CategorySerializer, ProductSerializer, StockMovementCreateSerializer, StockMovementSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [InventoryWritePermission]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [InventoryWritePermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "sku", "description"]
    ordering_fields = ["name", "quantity_in_stock", "unit_price", "created_at"]

    def perform_create(self, serializer):
        obj = serializer.save()
        log_activity(self.request, ActivityLog.Action.CREATE, "inventory", obj, "Product created")

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(self.request, ActivityLog.Action.UPDATE, "inventory", obj, "Product updated")

    def perform_destroy(self, instance):
        log_activity(self.request, ActivityLog.Action.DELETE, "inventory", instance, "Product deleted")
        instance.delete()


class StockMovementListCreateView(generics.ListCreateAPIView):
    """GET: full movement ledger (filterable by product).
    POST: records a movement AND atomically updates Product.quantity_in_stock
    inside a single DB transaction, using select_for_update() to lock the
    product row so concurrent stock-in/out requests can't race each other
    and leave quantity_in_stock inconsistent with the ledger."""

    queryset = StockMovement.objects.select_related("product", "created_by").all()
    permission_classes = [InventoryWritePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["product", "movement_type"]
    ordering_fields = ["created_at"]

    def get_serializer_class(self):
        return StockMovementCreateSerializer if self.request.method == "POST" else StockMovementSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = StockMovementCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=data["product"].pk)

            if data["movement_type"] == StockMovement.MovementType.IN:
                signed_qty = data["quantity"]
            elif data["movement_type"] == StockMovement.MovementType.OUT:
                signed_qty = -data["quantity"]
            else:  # ADJUSTMENT - client-supplied value can be positive or negative
                signed_qty = data["quantity"]

            new_quantity = product.quantity_in_stock + signed_qty
            if new_quantity < 0:
                raise serializers.ValidationError(
                    {"quantity": f"Insufficient stock. Only {product.quantity_in_stock} units available."}
                )

            movement = StockMovement.objects.create(
                product=product,
                movement_type=data["movement_type"],
                quantity=signed_qty,
                notes=data.get("notes", ""),
                created_by=request.user,
            )
            product.quantity_in_stock = F("quantity_in_stock") + signed_qty
            product.save(update_fields=["quantity_in_stock"])
            product.refresh_from_db()

        log_activity(
            request, ActivityLog.Action.CREATE, "inventory", movement,
            f"Stock {data['movement_type']} of {signed_qty} for {product.sku}",
        )
        return Response(StockMovementSerializer(movement).data, status=201)
