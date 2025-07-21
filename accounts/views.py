from django.shortcuts import render, redirect
from .forms import UserCreationForm, UserLoginForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
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