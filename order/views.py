from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Product
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
# Create your views here.



class AddToCart(LoginRequiredMixin, View):


    def post(self, request, product_id):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        product = get_object_or_404(Product, id=product_id)
        quantity = request.POST.get('quantity', 1)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("تعداد باید بزرگتر از صفر باشد.")
        except (ValueError, TypeError):
            messages.error(request, "تعداد نامعتبر است.")
            return redirect("home:product", product_id = product.id)
        
        if created:
            if quantity > product.stock:
                messages.error(request, "موجودی کافی برای این محصول وجود ندارد.")
                return redirect("home:product", product_id=product.id)

            cart.add_to_cartitem(product=product, quantity=quantity)
            messages.success(request, f"{product.name} با موفقیت به سبد خرید اضافه شد.")
            return redirect("home:product", product_id=product.id)

        else:
            cart_item = Cart.objects.get(user=request.user).items.filter(product=product).first()
            if cart_item:
                quantity_with_cart_quantity = cart_item.quantity + quantity
                if quantity_with_cart_quantity > product.stock:
                    messages.error(request, "تعداد وارد شده از تعداد موجود در سبد خرید بیشتر است.")
                    return redirect("home:product", product_id=product.id)
            else:
                quantity_with_cart_quantity = quantity
                
            cart.add_to_cartitem(product=product, quantity=quantity)
            messages.success(request, f"{product.name} با موفقیت به سبد خرید اضافه شد.")
            return redirect("home:product", product.id)

        


class CartView(LoginRequiredMixin, View):
    template_name = 'order/html/cart.html'

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