"""نماذج التسجيل وتسجيل الدخول"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Role


class RegisterForm(UserCreationForm):
    """نموذج إنشاء حساب جديد"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "البريد الإلكتروني"}),
    )
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "الاسم الكامل"}),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "رقم الهاتف"}),
    )
    # الدور الافتراضي للمسجلين الجدد: موظف مبيعات
    role = forms.ModelChoiceField(
        queryset=Role.objects.exclude(name=Role.RoleName.ADMIN),  # منع تسجيل مدير من الواجهة
        empty_label="اختر دورك",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "كلمة المرور"}),
    )
    password2 = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "تأكيد كلمة المرور"}),
    )

    class Meta:
        model = User
        fields = ["email", "full_name", "phone", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """نموذج تيل الدخول (بالبريد + كلمة المرور)"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "البريد الإلكتروني"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "كلمة المرور"}),
    )
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())
