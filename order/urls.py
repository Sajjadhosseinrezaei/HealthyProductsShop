from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'order'

urlpatterns = [
    path('cart/detail', views.CartView.as_view(), name='cart_detail'),
    path('cart/add/<int:product_id>/', views.AddToCart.as_view(), name='cart_add'),
    path('cart/update/<int:item_id>/' ,views.UpdateCartItemView.as_view(), name='cart_update' ),
    path('cart/remove/<int:item_id>/', views.RemoveCartItemView.as_view(), name='cart_remove'),

    path('', views.OrderListView.as_view(), name='order_lsit'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('create/', views.CreateOrderView.as_view(), name='create_order'),
    path('<int:order_id>/pay/', views.PaymentView.as_view(), name='payment'),
]
