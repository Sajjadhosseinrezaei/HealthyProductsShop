from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('create', views.CreateUserView.as_view(), name='create'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
]

