from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)  # slug را فقط خواندنی می‌کند

admin.site.register(Product)
admin.site.register(ProductImage)