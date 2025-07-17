from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

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
    مدل برای نگهداری آدرس‌های پستی کاربران.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses', verbose_name="کاربر")
    title = models.CharField(max_length=100, verbose_name="عنوان آدرس (مثلاً خانه)")
    recipient_name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی گیرنده")
    phone_number = models.CharField(max_length=11, verbose_name="شماره تماس")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    street = models.TextField(verbose_name="خیابان/کوچه و پلاک")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    details = models.TextField(blank=True, null=True, verbose_name="توضیحات بیشتر")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

    def __str__(self):
        return f"آدرس '{self.title}' برای کاربر {self.user.username}"