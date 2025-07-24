from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'order'

urlpatterns = [
    path('cart/detail', views.CartView.as_view(), name='cart_detail'),
    path('cart/add/<int:product_id>/', views.AddToCart.as_view(), name='cart_add'),
]
