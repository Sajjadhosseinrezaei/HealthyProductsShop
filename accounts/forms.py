from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(
        attrs={'class': 'form-control m-3 is-invalid', 'placeholder': 'رمز خود را وارد کنید'}))
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput(
        attrs={'class': 'form-control m-3 is-invalid', 'placeholder': 'تکرار رمز عبور'}))


    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email']

        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'username': 'نام کاربری',
            'email': 'ایمیل',
        }
        
        widgets = {
          
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control m-3', 
                    'placeholder': 'نام خود را وارد کنید'
                }
            ),
       
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control m-3', 
                    'placeholder': 'نام خانوادگی خود را وارد کنید'
                }
            ),
      
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control m-3', 
                    'placeholder': 'یک نام کاربری انتخاب کنید'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control m-3', 
                    'placeholder': 'ایمیل خود را وارد کنید'
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            raise ValidationError("ایمیل از قبل وجود دارد!")
        return email

    def clean_username(self):
        """
        اعتبارسنجی اختصاصی برای فیلد نام کاربری.
        """
        # ۱. دریافت نام کاربری تمیز شده از فرم
        username = self.cleaned_data.get('username')

        # ۲. بررسی قوانین دلخواه
        if ' ' in username:
            raise forms.ValidationError("نام کاربری نمی‌تواند حاوی فاصله باشد.", code='invalid_space')
        
        if len(username) < 5:
            raise forms.ValidationError("نام کاربری باید حداقل ۵ کاراکتر باشد.", code='min_length')

        # ۳. بررسی یکتا بودن (مهم‌ترین بخش)
        # این کوئری تمام کاربرانی را که همین نام کاربری را دارند (بدون توجه به بزرگی و کوچکی حروف) پیدا می‌کند
        queryset = CustomUser.objects.filter(username__iexact=username)

        # اگر فرم برای ویرایش کاربر باشد (نه ساخت کاربر جدید)
        # باید خود کاربر فعلی را از این بررسی مستثنی کنیم
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        # اگر با این شرایط هنوز کاربری با این نام وجود داشت، یعنی تکراری است
        if queryset.exists():
            raise forms.ValidationError("این نام کاربری قبلاً انتخاب شده است.", code='duplicate_username')

        # ۴. در نهایت، مقدار تمیز شده را برگردان
        return username

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError("پسوردها یکی نیست دوباره تلاش کنید")
        return self.cleaned_data['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user
    

class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control m-3',
            'placeholder': 'نام کاربری خود را وارد کنید'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control m-3',
            'placeholder': 'رمز عبور خود را وارد کنید'
        })
    )
