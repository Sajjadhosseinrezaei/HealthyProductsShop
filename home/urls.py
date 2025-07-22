from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products', views.ProductListView.as_view(), name='products'),
    path('product/<int:id>/', views.DetailView.as_view(), name='product'),
]
