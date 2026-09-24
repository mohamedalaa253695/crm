from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    filter_horizontal = ("permissions",)   # واجهة اختيار الصلاحيات


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "full_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("المعلومات الشخصية", {"fields": ("full_name", "phone")}),
        ("الصلاحيات", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تواريخ مهمة", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "role", "password1", "password2"),
        }),
    )
    search_fields = ("email", "full_name")
