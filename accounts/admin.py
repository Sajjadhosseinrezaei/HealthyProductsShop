from django.contrib import admin
from .models import CustomUser, Address
# Register your models here.



admin.site.register(CustomUser)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'street', 'postal_code', 'is_default']
    list_filter = ['is_default', 'city']
    search_fields = ['city', 'street', 'postal_code', 'user__username']