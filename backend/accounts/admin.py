from django.contrib import admin

from .models import ActivityLog, Profile

admin.site.register(Profile)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module", "object_repr")
    list_filter = ("action", "module")
    search_fields = ("object_repr", "user__username")
