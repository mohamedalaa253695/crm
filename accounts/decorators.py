"""Decorators للتحقق من الأدوار والصلاحيات على مستوى الـ View"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    الاستخدام:
        @role_required("ADMIN", "SALES")
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.has_role(*allowed_roles):
                raise PermissionDenied("هذه الصفحة غير متاحة لدورك الوظيفي.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(perm_codename):
    """تحقق من صلاحية Django رسمية (مثال: 'accounts.view_user')"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(perm_codename):
                raise PermissionDenied(f"صلاحية مطلوبة: {perm_codename}")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
