from django.contrib import admin
from .models import PaymentCard, Order, OrderItem, Cart, CartItem, Discount

@admin.register(PaymentCard)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ('card_holder', 'card_number', 'bank_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'bank_name')
    search_fields = ('card_holder', 'card_number')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at', 'payment_tracking_code')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'payment_tracking_code')
    date_hierarchy = 'created_at'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    list_filter = ('order', 'product__category')
    search_fields = ('product__name', 'order__id')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart__user', 'product__category')
    search_fields = ('product__name', 'cart__user__username')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'discount_type', 'is_active', 'min_purchase_amount')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)
