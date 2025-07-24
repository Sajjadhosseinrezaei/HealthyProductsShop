from django.db import models
from accounts.models import CustomUser, Address
from home.models import Product
from django.utils import timezone

class Cart(models.Model):
    """
    سبد خرید هر کاربر. هر کاربر یک سبد خرید فعال دارد.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart', verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    def __str__(self):
        return f"سبد خرید کاربر {self.user.username}"
    
    def get_total_price(self):
        total = sum(item.total_price() for item in self.items.all())
        return total
    

    def add_to_cartitem(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={
                'price': product.final_price,
                'quantity': quantity
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price = product.final_price
            cart_item.save()


    def remove_empty_cart(self):
        if not self.items.exists():
            self.delete()

class CartItem(models.Model):
    """
    یک آیتم (محصول و تعداد آن) در سبد خرید.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="سبد خرید")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت')


    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ('cart', 'product') # جلوگیری از افزودن محصول تکراری به سبد

    def __str__(self):
        return f"{self.quantity} عدد از محصول '{self.product.name}'"

    @property
    def total_price(self):
        """مجموع قیمت این آیتم (قیمت محصول * تعداد)."""
        return self.quantity * self.product.final_price
    
    def update_cart_quantity(self, quantity):
        if quantity < 1:
            raise ValueError("تعداد نمی‌تواند کمتر از 1 باشد")
        if quantity <= self.product.stock:
            self.quantity = quantity
            self.save()
        else:
            raise ValueError("تعداد درخواستی بیشتر از موجودی است")


class Order(models.Model):
    """
    یک سفارش ثبت‌شده توسط کاربر.
    """
    STATUS_CHOICES = (
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
        ('cancelled', 'لغو شده'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name="کاربر")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name="آدرس ارسال")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ کل سفارش")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name="وضعیت سفارش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ سفارش")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        user_info = self.user.username if self.user else 'کاربر حذف شده'
        return f"سفارش شماره {self.id} برای کاربر {user_info}"

class OrderItem(models.Model):
    """
    یک آیتم در یک سفارش ثبت‌شده. قیمت محصول در زمان خرید ذخیره می‌شود.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="محصول")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت واحد در زمان خرید")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        product_info = self.product.name if self.product else 'محصول حذف شده'
        return f"{self.quantity} عدد از '{product_info}' در سفارش {self.order.id}"


# ---------------------------------
# ۴. مدل تخفیف‌ها
# ---------------------------------

class Discount(models.Model):
    """
    مدیریت کدهای تخفیف درصدی یا با مبلغ ثابت.
    """
    TYPE_CHOICES = (
        ('percent', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    )

    code = models.CharField(max_length=50, unique=True, verbose_name="کد تخفیف")
    discount_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="نوع تخفیف")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مقدار (درصد یا مبلغ)")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع اعتبار")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان اعتبار")
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True, verbose_name="حداقل مبلغ خرید")
    one_time_use_per_user = models.BooleanField(default=False, verbose_name="قابلیت استفاده یکبار برای هر کاربر")
    used_by = models.ManyToManyField(CustomUser, blank=True, related_name='used_discounts', verbose_name="استفاده شده توسط کاربران")
    is_active = models.BooleanField(default=True, verbose_name="فعال/غیرفعال")

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

    def __str__(self):
        return self.code

    def is_valid(self):
        """بررسی می‌کند آیا کد تخفیف در حال حاضر معتبر است یا خیر."""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
