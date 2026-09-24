"""
نماذج نظام المستخدمين والصلاحيات (RBAC)

الفكرة:
- نموذج Role (الدور): يمثل وظيفة داخل الشركة (مدير/مبيعات/دعم)
  ويرتبط بصلاحيات Django الرسمية عبر ManyToMany مع Permission.
- نموذج User: مستخدم مخصص يرتبط بدور واحد (يمكن تطويره لأدوار متعددة).
- دالة has_perm على المستوى الدور، ونستخدم Django Group
  لمزامنة الصلاحيات مع نظام django.contrib.auth لتعمل مع
  has_perm() الخاصة بالمستخدم ولوحة التحكم.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, Group, Permission, BaseUserManager
)
from django.core.exceptions import PermissionDenied


class Role(models.Model):
    """الأدوار الأساسية داخل النظام"""

    class RoleName(models.TextChoices):
        ADMIN = "ADMIN", "مدير النظام"
        SALES = "SALES", "موظف مبيعات"
        SUPPORT = "SUPPORT", "دعم فني"

    name = models.CharField(max_length=20, choices=RoleName.choices, unique=True)
    description = models.TextField(blank=True, verbose_name="وصف الدور")

    # الصلاحيات الرسمية لـ Django المرتبطة بهذا الدور
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles",
        verbose_name="الصلاحيات",
    )

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        default_permissions = ("add", "change", "delete", "view")

    def __str__(self):
        return self.get_name_display()

    def sync_django_group(self):
        """مزامنة الدور مع Group بنفس الاسم لتعمل صلاحيات Django."""
        group, _ = Group.objects.get_or_create(name=self.name)
        group.permissions.set(self.permissions.all())
        return group


class UserManager(BaseUserManager):
    """مدير مخصص لنموذج المستخدم للتعامل مع البريد الإلكتروني كمعرف أساسي"""
    
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("يجب إدخال البريد الإلكتروني")
        
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    المستخدم المخصص:
    - نحافظ على كل حقول AbstractBaseUser (كلمة المرور، آخر دخول...)
    - PermissionsMixin تضيف is_superuser + groups + user_permissions
    """
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    full_name = models.CharField(max_length=150, verbose_name="الاسم الكامل")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="الدور الوظيفي",
    )
    
    objects = UserManager() # تعيين المدير المخصص بشكل صحيح
    
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_staff = models.BooleanField(default=False, verbose_name="طاقم العمل")

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"          # تسجيل الدخول بالبريد الإلكتروني
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def save(self, *args, **kwargs):
        """عند الحفظ: مدير النظام يصبح staff + superuser تلقائياً."""
        if self.role and self.role.name == Role.RoleName.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def has_role(self, *role_names):
        """التحقق من أن المستخدم يمتلك أحد الأدوار المطلوبة."""
        return self.role and self.role.name in role_names

    @property
    def role_display(self):
        return self.role.get_name_display() if self.role else "بدون دور"


def check_permission(user, perm_codename):
    """دالة مساعدة: ترفع PermissionDenied إذا لم يمتلك المستخدم الصلاحية."""
    if not user.has_perm(perm_codename):
        raise PermissionDenied(f"لا تملك صلاحية: {perm_codename}")