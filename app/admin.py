# Register your models here.
from django.contrib import admin
from .models import CustomUser, JsonFileModel, InferenceModel, LoginHistoryModel


# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    fields = ('username', 'first_name', 'last_name', 'email', 'location', 'contact', 'is_admin', 'bio', 'profile_picture')

class InferenceModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'disaster_date', 'disaster_city', 'disaster_state', 'disaster_country', 'disaster_type', 'disaster_description', 'disaster_comments', 'tif_middle_latitude', 'tif_middle_longitude', 'pre_tif_path', 'post_tif_path', 'results']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InferenceModel, InferenceModelAdmin)
admin.site.register(JsonFileModel)
admin.site.register(LoginHistoryModel)
