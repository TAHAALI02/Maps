from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active", 'road_edit_permission', 'road_delete_permission', 'property_edit_permission', 'property_delete_permission')
    list_filter = ("role", "is_staff", "is_active", "gender", 'road_edit_permission', 'road_delete_permission', 'property_edit_permission', 'property_delete_permission')
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "date_of_birth", "gender")}),
        ("Role & Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions", "road_permission", "property_permission")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )
    readonly_fields = ("date_joined",)


admin.site.register(CustomUser, CustomUserAdmin)



from .models import MapFeature


@admin.register(MapFeature)
class MapFeatureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feature_type",
        "name",
        "creator",
        "status",
        "reviewer",
        "delete_requested",
        "deleted",
        "created_at",
    )

    list_filter = (
        "feature_type",
        "status",
        "delete_requested",
        "deleted",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "creator__username",
        "creator__email",
        "reviewer__username",
    )

    readonly_fields = (
        "created_at",
        "reviewed_at",
        "published_at",
    )

    autocomplete_fields = (
        "creator",
        "reviewer",
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("Feature Information", {
            "fields": (
                "feature_type",
                "name",
                "description",
            )
        }),

        ("Geometry & Style", {
            "fields": (
                "geometry",
                "style",
            )
        }),

        ("Approval", {
            "fields": (
                "creator",
                "status",
                "reviewer",
                "review_note",
            )
        }),

        ("Publishing", {
            "fields": (
                "published_snapshot",
                "published_at",
            )
        }),

        ("Delete Status", {
            "fields": (
                "delete_requested",
                "deleted",
            )
        }),

        ("Dates", {
            "fields": (
                "created_at",
                "reviewed_at",
            )
        }),
    )

    actions = (
        "approve_features",
        "reject_features",
        "mark_deleted",
    )

    @admin.action(description="Approve selected features")
    def approve_features(self, request, queryset):
        queryset.update(status=MapFeature.STATUS_APPROVED)

    @admin.action(description="Reject selected features")
    def reject_features(self, request, queryset):
        queryset.update(status=MapFeature.STATUS_REJECTED)

    @admin.action(description="Mark selected features as deleted")
    def mark_deleted(self, request, queryset):
        queryset.update(deleted=True)