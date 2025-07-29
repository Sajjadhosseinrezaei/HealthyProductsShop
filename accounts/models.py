from django.db import models
from django.contrib.auth.models import AbstractUser



# ---------------------------------
# ۱. مدل‌های کاربران و آدرس‌ها
# ---------------------------------

class CustomUser(AbstractUser):
    """
    مدل سفارشی کاربر با قابلیت تعیین نقش (مشتری یا ادمین).
    فیلدهای اصلی مانند نام کاربری، ایمیل و رمز عبور از AbstractUser به ارث برده می‌شوند.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'مشتری'
        ADMIN = 'ADMIN', 'ادمین'

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER, verbose_name="نقش کاربری")

    def __str__(self):
        return self.username



class Address(models.Model):
    """
    مدل برای ذخیره اطلاعات آدرس کاربران.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses', verbose_name="کاربر")
    city = models.CharField(max_length=100, verbose_name="شهر")
    street = models.CharField(max_length=255, verbose_name="خیابان")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    is_default = models.BooleanField(default=False, verbose_name="آدرس پیش‌فرض")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"{self.city}, {self.street}, {self.postal_code} ({self.user.username})"

    def save(self, *args, **kwargs):
        """
        اطمینان از اینکه فقط یک آدرس به عنوان پیش‌فرض برای هر کاربر تنظیم شده است.
        """
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)