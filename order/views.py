from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Product, Order, OrderItem, Discount, PaymentCard
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, View
from accounts.models import Address
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
# Create your views here.


class AddToCart(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # ۱. دریافت آبجکت‌های مورد نیاز
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        # ۲. اعتبارسنجی تعداد ورودی
        try:
            quantity_to_add = int(request.POST.get('quantity', 1))
            if quantity_to_add <= 0:
                messages.error(request, "تعداد باید عددی مثبت باشد.")
                # --- تغییر در اینجا ---
                return redirect("home:product", id=product.id)
        except (ValueError, TypeError):
            messages.error(request, "تعداد وارد شده نامعتبر است.")
            # --- تغییر در اینجا ---
            return redirect("home:product", id=product.id)
            
        # ۳. پیدا کردن آیتم موجود در سبد (در صورت وجود)
        cart_item = cart.items.filter(product=product).first()
        
        # ۴. محاسبه تعداد فعلی و تعداد نهایی
        current_quantity = cart_item.quantity if cart_item else 0
        final_quantity = current_quantity + quantity_to_add

        # ۵. بررسی نهایی موجودی انبار (مهم‌ترین بخش)
        if final_quantity > product.stock:
            messages.error(request, f"موجودی محصول ({product.stock} عدد) برای این تعداد کافی نیست.")
            # --- تغییر در اینجا ---
            return redirect("home:product", id=product.id)
            
        # ۶. افزودن به سبد خرید (با استفاده از متد مدل)
        cart.add_to_cartitem(product=product, quantity=quantity_to_add)
        
        messages.success(request, f'"{product.name}" با موفقیت به سبد شما اضافه شد.')
        # --- تغییر در اینجا ---
        return redirect("order:cart_detail")
 

        


class CartView(LoginRequiredMixin, View):
    template_name = 'order/html/cart.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "برای مشاهده سبد خرید باید وارد شوید")
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            cart = None

        if cart:
            cart_items = cart.items.select_related('product', 'product__category').prefetch_related('product__images')
            total_price = cart.get_total_price
            for item in cart_items:
                item.subtotal = item.total_price
        else:
            cart_items = None
            total_price = 0

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }
        return render(request, self.template_name, context)
    

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        # ۱. پیدا کردن آیتم مورد نظر در سبد کاربر
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # ۲. دریافت تعداد جدید از فرم
        try:
            new_quantity = int(request.POST.get('quantity'))
        except (ValueError, TypeError):
            messages.error(request, "مقدار نامعتبر است.")
            return redirect('order:cart_detail')

        # ۳. اگر کاربر تعداد را صفر یا منفی وارد کرد، آیتم را حذف کن
        if new_quantity <= 0:
            cart_item.delete()
            messages.success(request, "محصول از سبد شما حذف شد.")
            return redirect('order:cart_detail')
            
        # ۴. بررسی موجودی انبار در برابر تعداد جدید
        if new_quantity > cart_item.product.stock:
            messages.error(request, f"موجودی محصول ({cart_item.product.stock} عدد) کافی نیست.")
            return redirect('order:cart_detail')
            
        # ۵. به‌روزرسانی تعداد به مقدار جدید (منطق جایگزینی)
        cart_item.quantity = new_quantity
        cart_item.save()
        
        messages.success(request, "سبد خرید شما با موفقیت به‌روزرسانی شد.")
        return redirect('order:cart_detail')
    
class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        # ۱. آیتم مورد نظر را با امنیت کامل پیدا کن (حتما برای کاربر فعلی باشد)
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        # ۲. از متد داخلی .delete() خود جنگو استفاده کن
        cart_item.delete()

        # ۳. کاربر را به صفحه سبد خرید بازگردان
        return redirect('order:cart_detail')
    


class OrderListView(LoginRequiredMixin, ListView):

    """
    نمایش لیست سفارش های کاربر لاگین شده
    """
    model = Order
    template_name = 'order/html/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    

class OrderDetailView(LoginRequiredMixin, DetailView):
    
    """
    نمایش جزئیات یک سفارش خاص
    """

    model = Order
    template_name = 'order/html/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    

class CreateOrderView(LoginRequiredMixin, View):
    """
    ثبت سفارش از سبد خرید و افزودن آدرس جدید
    """
    template_name = 'order/html/create_order.html'

    def get(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=self.request.user)
        if not cart.items.exists():
            messages.error(self.request, "سبد خرید شما خالی است.")
            return redirect('order:cart_detail')  # استفاده از namespace 'order' برای هماهنگی با ویوهای شما
        addresses = Address.objects.filter(user=self.request.user)
        cart_items = cart.items.select_related('product', 'product__category').prefetch_related('product__images')  # هماهنگی با CartView
        total_price = cart.get_total_price()  # استفاده از متد get_total_price
        for item in cart_items:
            item.subtotal = item.total_price  # محاسبه subtotal مشابه CartView
        return render(request, self.template_name, {
            'cart': cart,
            'addresses': addresses,
            'cart_items': cart_items,
            'total_price': total_price
        })

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=self.request.user)
        if not cart.items.exists():
            messages.error(self.request, "سبد خرید شما خالی است.")
            return redirect('order:cart_detail')

        address_id = self.request.POST.get('address')
        city = self.request.POST.get('city')
        street = self.request.POST.get('street')
        postal_code = self.request.POST.get('postal_code')
        is_default = self.request.POST.get('is_default') == 'on'
        discount_code = self.request.POST.get('discount_code')

        # انتخاب یا ایجاد آدرس
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=self.request.user)
        elif city and street and postal_code:
            address = Address.objects.create(
                user=self.request.user,
                city=city,
                street=street,
                postal_code=postal_code,
                is_default=is_default
            )
        else:
            messages.error(self.request, "لطفاً یک آدرس انتخاب کنید یا اطلاعات آدرس جدید را وارد کنید.")
            return redirect('order:create_order')

        # محاسبه مبلغ کل
        total_amount = cart.get_total_price()

        # بررسی کد تخفیف
        discount = None
        if discount_code:
            try:
                discount = Discount.objects.get(code=discount_code, is_active=True)
                if not discount.is_valid():
                    messages.error(self.request, "کد تخفیف معتبر نیست یا منقضی شده است.")
                elif discount.one_time_use_per_user and discount.used_by.filter(id=self.request.user.id).exists():
                    messages.error(self.request, "این کد تخفیف قبلاً توسط شما استفاده شده است.")
                elif discount.min_purchase_amount and total_amount < discount.min_purchase_amount:
                    messages.error(self.request, f"مبلغ سفارش باید حداقل {discount.min_purchase_amount} تومان باشد.")
                else:
                    if discount.discount_type == 'percent':
                        discount_amount = total_amount * (discount.value / 100)
                        total_amount -= discount_amount
                    else:  # fixed
                        total_amount -= discount.value
                    if total_amount < 0:
                        total_amount = 0
            except Discount.DoesNotExist:
                messages.error(self.request, "کد تخفیف نامعتبر است.")

        # ایجاد سفارش با استفاده از تراکنش اتمیک
        with transaction.atomic():
            order = Order.objects.create(
                user=self.request.user,
                shipping_address=address,
                total_amount=total_amount,
                status='pending_payment',
                created_at=timezone.now()
            )

            # انتقال آیتم‌های سبد خرید به سفارش
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.final_price
                )

            # ثبت استفاده از کد تخفیف
            if discount and discount.is_valid():
                discount.used_by.add(self.request.user)

            # خالی کردن سبد خرید
            cart.items.all().delete()
            cart.delete()

        messages.success(self.request, f"سفارش شماره {order.id} با موفقیت ثبت شد.")
        return redirect(reverse('order:order_detail', kwargs={'pk': order.id}))
    


class PaymentView(LoginRequiredMixin, View):
    """
    نمایش صفحه پرداخت و پردازش کد پیگیری برای سفارش
    """
    template_name = 'order/html/payment.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment_card = PaymentCard.objects.filter(is_active=True).first()  # دریافت اولین کارت فعال
        if not payment_card:
            messages.error(request, "هیچ کارت پرداختی فعالی تنظیم نشده است.")
            return redirect('order:order_detail', pk=order_id)
        return render(request, self.template_name, {
            'order': order,
            'payment_card': payment_card,
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment_card = PaymentCard.objects.filter(is_active=True).first()
        tracking_code = request.POST.get('tracking_code')

        if not tracking_code:
            messages.error(request, "لطفاً کد پیگیری را وارد کنید.")
            return render(request, self.template_name, {
                'order': order,
                'payment_card': payment_card,
            })

        # لاجیک ساده برای تأیید کد پیگیری (می‌توانید با سیستم واقعی جایگزین کنید)
        # اینجا فرض می‌کنیم کد پیگیری باید 10 رقم باشد و منحصربه‌فرد باشد
        try:
            tracking_code = int(tracking_code)
            if len(str(tracking_code)) != 10:
                messages.error(request, "کد پیگیری باید 10 رقم باشد.")
                return render(request, self.template_name, {
                    'order': order,
                    'payment_card': payment_card,
                })
            # شبیه‌سازی تأیید (در واقعیت باید با بانک یا سیستم پرداخت چک شود)
            order.payment_tracking_code = tracking_code
            order.status = 'processing'
            order.save()
            messages.success(request, f"پرداخت سفارش شماره {order.id} با موفقیت تأیید شد.")
            return redirect('order:order_detail', pk=order_id)
        except ValueError:
            messages.error(request, "کد پیگیری باید عددی باشد.")
            return render(request, self.template_name, {
                'order': order,
                'payment_card': payment_card,
            })