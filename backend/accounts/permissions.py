from rest_framework import permissions


def _role(request):
    return getattr(getattr(request.user, "profile", None), "role", None)


class IsAdmin(permissions.BasePermission):
    """Full-access role only."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and (
            request.user.is_superuser or _role(request) == "admin"
        )


class IsAdminOrManager(permissions.BasePermission):
    """Employees module: admin has full access, manager can manage employees."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser or _role(request) in ("admin", "manager"):
            return True
        return request.method in permissions.SAFE_METHODS


class InventoryWritePermission(permissions.BasePermission):
    """Inventory module: admin/inventory roles can write, everyone
    authenticated can read (sales staff need read access to check stock)."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or _role(request) in ("admin", "inventory")


class SalesWritePermission(permissions.BasePermission):
    """Sales module: admin/sales roles can write, everyone authenticated
    can read (managers/inventory need visibility into sales)."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or _role(request) in ("admin", "sales")


class ReportsAndLogsPermission(permissions.BasePermission):
    """Reports & Activity Logs: admin and manager only."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.is_superuser or _role(request) in ("admin", "manager")
