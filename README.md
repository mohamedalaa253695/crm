# نظام CRM — Django

## خطوات التشغيل

```bash
python -m venv venv
source venv/bin/activate        # على ويندوز: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # أنشئ المدير
python manage.py runserver
```

## إنشاء الأدوار والصلاحيات

بعد أول تشغيل، افتح: http://127.0.0.1:8000/admin

1. أنشئ 3 أدوار (Role): ADMIN / SALES / SUPPORT
2. اربط بكل دور الصلاحيات المناسبة (filter_horizontal)
3. عند حفظ الدور، استخدم الدالة role.sync_django_group() لمزامنة Group

## استعادة كلمة المرور

أثناء التطوير تظهر رسائل البريد في الطرفية (Console backend).
في الإنتاج: فعّل إعدادات SMTP في settings.py.
