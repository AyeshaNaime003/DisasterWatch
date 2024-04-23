from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    # additional fields for user
    location = models.TextField(null=True, blank=True)
    contact = models.TextField(max_length=14, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default_profile_pic.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def _str_(self):
        return self.username
    
class JsonFileModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    json_file = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # You can add more fields as needed

    def _str_(self):
        return f"JsonFileModel - {self.id} (User: {self.user.username})"