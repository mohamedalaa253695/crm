"""واجهات المصادقة: تسجيل / دخول / خروج / استعادة كلمة المرور"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm
from .decorators import role_required


class CustomLoginView(LoginView):
    """تسجيل الدخول — نستخدم قالب Django الافتراضي في registration/login.html"""
    template_name = "registration/login.html"
    redirect_authenticated_user = True




def register_view(request):
    """إنشاء حساب جديد"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # تسجيل الدخول تلقائياً بعد التسجيل
            messages.success(request, f"مرحباً {user.full_name}! تم إنشاء حسابك بنجاح.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, "تم تسجيل خروجك بنجاح.")
    return redirect("login")


#@role_required("ADMIN", "SALES", "SUPPORT")
def dashboard(request):
    """لوحة التحكم — متاحة لجميع الأدوار (مثال)"""
    return render(request, "dashboard.html", {"user": request.user})




# ========== استعادة كلمة المرور (Views جاهزة من Django) ==========

class CustomPasswordResetView(PasswordResetView):
    """
    1) نموذج إدخال البريد الإلكتروني
    2) Django يرسل بريداً يحتوي على رابط مؤقت (token)
    """
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """رسالة تأكيد أن البريد تم إرساله"""
    template_name = "registration/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """نموذج إدخال كلمة المرور الجديدة بعد الضغط على رابط البريد"""
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """رسالة نجاح إعادة التعيين"""
    template_name = "registration/password_reset_complete.html"
