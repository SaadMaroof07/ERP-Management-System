from django.db import transaction
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import ActivityLog, log_activity
from accounts.permissions import SalesWritePermission
from inventory.models import Product, StockMovement

from .models import Customer, Sale, SaleItem
from .serializers import CustomerSerializer, SaleCreateSerializer, SaleSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [SalesWritePermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "phone"]


class SaleViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Sales are created only through the /checkout/ action (never a plain
    POST), because creating a sale has side effects - stock deduction,
    total calculation - that a generic create endpoint shouldn't allow a
    client to bypass or tamper with."""

    queryset = Sale.objects.select_related("customer", "created_by").prefetch_related("items").all()
    serializer_class = SaleSerializer
    permission_classes = [SalesWritePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "customer"]
    ordering_fields = ["created_at", "total_amount"]

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        input_serializer = SaleCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        with transaction.atomic():
            total = 0
            sale = Sale.objects.create(
                customer=data.get("customer"), notes=data.get("notes", ""),
                total_amount=0, created_by=request.user,
            )

            for line in data["items"]:
                product = Product.objects.select_for_update().get(pk=line["product"].pk)
                qty = line["quantity"]

                if product.quantity_in_stock < qty:
                    transaction.set_rollback(True)
                    return Response(
                        {"detail": f"Insufficient stock for {product.name}. Only {product.quantity_in_stock} available."},
                        status=400,
                    )

                SaleItem.objects.create(
                    sale=sale, product=product, product_name=product.name,
                    unit_price=product.unit_price, quantity=qty,
                )
                StockMovement.objects.create(
                    product=product, movement_type=StockMovement.MovementType.OUT,
                    quantity=-qty, reference=f"Sale #{sale.id}", created_by=request.user,
                )
                product.quantity_in_stock = F("quantity_in_stock") - qty
                product.save(update_fields=["quantity_in_stock"])

                total += product.unit_price * qty

            sale.total_amount = total
            sale.save(update_fields=["total_amount"])

        log_activity(request, ActivityLog.Action.CREATE, "sales", sale, f"Sale of {total} recorded")
        return Response(SaleSerializer(sale).data, status=201)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancels a completed sale and restocks every item, inside one
        transaction so a partial cancellation can never happen."""
        sale = self.get_object()
        if sale.status == Sale.Status.CANCELLED:
            return Response({"detail": "Sale is already cancelled."}, status=400)

        with transaction.atomic():
            for item in sale.items.select_related("product"):
                if item.product:
                    product = Product.objects.select_for_update().get(pk=item.product.pk)
                    StockMovement.objects.create(
                        product=product, movement_type=StockMovement.MovementType.IN,
                        quantity=item.quantity, reference=f"Sale #{sale.id} cancelled", created_by=request.user,
                    )
                    product.quantity_in_stock = F("quantity_in_stock") + item.quantity
                    product.save(update_fields=["quantity_in_stock"])
            sale.status = Sale.Status.CANCELLED
            sale.save(update_fields=["status"])

        log_activity(request, ActivityLog.Action.UPDATE, "sales", sale, "Sale cancelled and stock restored")
        return Response(SaleSerializer(sale).data)
