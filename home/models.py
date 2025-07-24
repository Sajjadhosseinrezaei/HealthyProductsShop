from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """
    دسته‌بندی محصولات با استفاده از django-mptt برای کارایی بالا در ساختار درختی.
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="اسلاگ (برای URL)")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True, verbose_name="دسته‌بندی والد")

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    مدل اصلی برای تعریف یک محصول در فروشگاه.
    """
    STATUS_CHOICES = (
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
    )

    name = models.CharField(max_length=255, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات کامل")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت اصلی (تومان)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت پس از تخفیف (تومان)")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="دسته‌بندی")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت محصول")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    is_featured = models.BooleanField(default=False, verbose_name="محصول ویژه")
    
    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """قیمت نهایی محصول را با در نظر گرفتن تخفیف برمی‌گرداند."""
        if self.discount_price is not None and self.discount_price > 0:
            return self.discount_price
        if self.price is not None:
            return self.price
        return 0  # مقدار پیش‌فرض ایمن
    
    
class ProductImage(models.Model):
    """
    مدل برای مدیریت تصاویر متعدد برای هر محصول.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    image = models.ImageField(upload_to='products/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="متن جایگزین (Alt Text)")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"

    def __str__(self):
        return f"تصویر برای محصول {self.product.name}"
