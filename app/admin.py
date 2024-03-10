# Register your models here.
from django.contrib import admin
from .models import CustomUser, JsonFileModel

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    fields = ('username', 'first_name', 'last_name', 'email', 'location', 'contact', 'is_admin', 'bio', 'profile_picture')
    # search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(JsonFileModel)