from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Product
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
# Create your views here.



from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, Cart, CartItem

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
        return redirect("home:product", id=product.id)
 

        


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