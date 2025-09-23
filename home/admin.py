from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)  # slug را فقط خواندنی می‌کند

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'status', 'is_featured', 'properties_list')
    list_filter = ('status', 'is_featured', 'properties', 'category')
    search_fields = ('name', 'description', 'properties__name')
    filter_horizontal = ('properties',)  # برای انتخاب بهتر خواص در فرم ادمین
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(ProductImage)