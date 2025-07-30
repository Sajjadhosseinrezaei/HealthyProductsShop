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
    نمایش لیست محصولات با امکان فیلتر بر اساس دسته‌بندی
    """
    model = Product
    template_name = 'home/html/products.html'
    context_object_name = 'products'
    paginate_by = 10  # تعداد محصولات در هر صفحه

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active')  # فقط محصولات فعال
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # لیست همه دسته‌بندی‌ها برای فیلتر
        return context

class DetailView(View):


    template_name = 'home/html/product_detail.html'
    model = Product

    def get(self, request, id):
        product = self.model.objects.get(pk=id)

        return render(request, self.template_name, {'product':product})