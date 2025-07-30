from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserCreationForm, UserLoginForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, Address
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from order.models import Cart, Order, CartItem
# Create your views here.

class CreateUserView(View):

    template_name = 'accounts/html/createUser.html'
    form_class = UserCreationForm

    def get(self, request):
        return render(request, self.template_name, {'form':self.form_class})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = CustomUser.objects.create_user(first_name=cd['first_name'], last_name=cd['last_name'],username=cd['username'], email=cd['email'],
                                            password=cd['password2'])
            user = authenticate(email=cd['email'], password=cd['password2'])
            if user is not None:
                login(request, user)
            messages.success(request, 'شما ثبت نام شدید')
            return redirect('home:home')

        return render(request, self.template_name, {'form': form})
    
    
class UserLoginView(View):
    template_name = 'accounts/html/login.html'
    form_class = UserLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'شما قبلاً وارد شده‌اید.')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self , request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "با موفقیت وارد شدید")
                return redirect('home:home')
            else:
                messages.error(request, 'اطلاعات وارد شده نادرست است.')
        return render(request, self.template_name, {'form': form})
    

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'با موفقیت خارج شدید.')
        return redirect('home:home')
    


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    fields = ['city', 'street', 'postal_code', 'is_default']
    template_name = 'accounts/html/address_form.html'
    success_url = reverse_lazy('order:cart_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "آدرس با موفقیت اضافه شد.")
        return super().form_valid(form)
    
class ProfileView(LoginRequiredMixin, View):
    """
    نمایش صفحه پروفایل کاربر با اطلاعات کاربری، آدرس‌ها، سفارش‌ها و سبد خرید
    """
    template_name = 'accounts/html/profile.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        addresses = Address.objects.filter(user=user).order_by('-is_default', 'created_at')
        orders = Order.objects.filter(user=user).order_by('-created_at')  # لیست سفارش‌ها
        cart, created = Cart.objects.get_or_create(user=user)  # سبد خرید کاربر
        cart_items = CartItem.objects.filter(cart=cart)  # آیتم‌های سبد خرید
        return render(request, self.template_name, {
            'user': user,
            'addresses': addresses,
            'orders': orders,
            'cart': cart,
            'cart_items': cart_items,
        })

    
class AddressDeleteView(LoginRequiredMixin, View):
    """
    حذف آدرس کاربر
    """
    def post(self, request, address_id):
        address = get_object_or_404(Address, id=address_id, user=request.user)
        if address.is_default:
            messages.error(request, "نمی‌توانید آدرس پیش‌فرض را حذف کنید.")
        else:
            address.delete()
            messages.success(request, "آدرس با موفقیت حذف شد.")
        return redirect('accounts:profile')