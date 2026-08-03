from rest_framework import filters, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import ActivityLog
from .permissions import ReportsAndLogsPermission
from .serializers import ActivityLogSerializer, MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - public, always creates a low-privilege 'employee' role."""

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ - returns { access, refresh, user }, and writes a
    'login' ActivityLog entry so the audit trail includes authentication events."""

    permission_classes = [permissions.AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            User = get_user_model_lazy()
            username = request.data.get("username")
            try:
                user = User.objects.get(username=username)
                ActivityLog.objects.create(
                    user=user, action=ActivityLog.Action.LOGIN, module="auth",
                    object_repr=user.username, description="User logged in",
                    ip_address=request.META.get("REMOTE_ADDR"),
                )
            except User.DoesNotExist:
                pass
        return response


def get_user_model_lazy():
    from django.contrib.auth import get_user_model
    return get_user_model()


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ActivityLogListView(generics.ListAPIView):
    """GET /api/auth/activity-logs/ - admin/manager only, most recent first."""

    queryset = ActivityLog.objects.select_related("user").all()
    serializer_class = ActivityLogSerializer
    permission_classes = [ReportsAndLogsPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["module", "action", "object_repr", "user__username"]
    ordering_fields = ["created_at"]
