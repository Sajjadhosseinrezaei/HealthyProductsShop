from .models import Product, ProductImage, Category
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
# Create your views here.


class HomeView(View):

    template_name = 'home/html/home.html'


    def get(self, request):
        products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]
        return render(request, self.template_name, {'products':products})
    

class ProductListView(ListView):
    """
    نمایش لیست محصولات با استفاده از ListView برای خوانایی و کارایی بهتر.
    """
    model = Product  # ۱. مشخص کردن مدل
    template_name = 'home/html/products.html'  # ۲. مشخص کردن تمپلیت
    context_object_name = 'products'  # ۳. تغییر نام object_list به products در تمپلیت
    paginate_by = 10  # ۴. تعداد محصولات در هر صفحه

    def get_queryset(self):
        """
        کدها را طوری بازنویسی می‌کنیم که فقط محصولات فعال نمایش داده شوند.
        """
        return Product.objects.filter(status='active').order_by('-created_at')


class DetailView(View):


    template_name = 'home/html/product_detail.html'
    model = Product

    def get(self, request, id):
        product = self.model.objects.get(pk=id)

        return render(request, self.template_name, {'product':product})