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
    model = Product
    template_name = 'home/html/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active')
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                # شامل کردن دسته انتخاب‌شده و تمام زیرشاخه‌هایش
                descendants = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=descendants)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # برای نمایش وضعیت فعال/باز بودن منوی دسته‌ها
        category_slug = self.request.GET.get('category')
        if category_slug:
            selected = Category.objects.filter(slug=category_slug).first()
            if selected:
                # لیستی از slug‌های دسته انتخاب‌شده و اجدادش برای استفاده در تمپلیت
                ancestor_slugs = [c.slug for c in selected.get_ancestors(include_self=True)]
            else:
                ancestor_slugs = []
        else:
            selected = None
            ancestor_slugs = []

        context['selected_category'] = selected
        context['active_category_slugs'] = ancestor_slugs
        return context

class DetailView(View):


    template_name = 'home/html/product_detail.html'
    model = Product

    def get(self, request, id):
        product = self.model.objects.get(pk=id)

        return render(request, self.template_name, {'product':product})