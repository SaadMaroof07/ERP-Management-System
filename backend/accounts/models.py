from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extends Django's built-in User with an ERP role.

    Roles (least to most privileged, roughly):
      - employee:  default self-registration role; read-only own profile
      - sales:     manage the Sales module; read-only on Inventory
      - inventory: manage the Inventory module; read-only on Sales
      - manager:   manage Employees; read access to Reports & Activity Logs
      - admin:     full access to every module

    Using Django's built-in auth_user table (PBKDF2 password hashing,
    validators, etc.) instead of a hand-rolled table is itself a security
    decision - see docs for the Week 03 security/architecture write-up.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        SALES = "sales", "Sales"
        INVENTORY = "inventory", "Inventory"
        EMPLOYEE = "employee", "Employee"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class ActivityLog(models.Model):
    """Audit trail: one row per meaningful write action across the ERP.

    Written explicitly from each viewset's perform_create/update/destroy
    (rather than via signals) so every log entry can capture *who* made
    the change and a human-readable description, not just that a row
    changed somewhere.
    """

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="activity_logs"
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    module = models.CharField(max_length=50)          # e.g. "employees", "inventory", "sales"
    object_repr = models.CharField(max_length=255)    # human-readable label of the affected record
    description = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "action"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.user} {self.action} {self.module}: {self.object_repr}"


def log_activity(request, action, module, obj, description=""):
    """Convenience helper called from viewsets to write one ActivityLog row.

    `obj` just needs a sensible __str__; we never persist entire objects,
    only a short human-readable representation.
    """
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        module=module,
        object_repr=str(obj)[:255],
        description=description,
        ip_address=_client_ip(request),
    )


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
