from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('create', views.CreateUserView.as_view(), name='create'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    path('address/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/delete/<int:address_id>/', views.AddressDeleteView.as_view(), name='address_delete'),
]

