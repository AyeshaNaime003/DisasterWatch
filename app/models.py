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

class InferenceModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    disaster_date = models.DateField(null=False)
    disaster_city = models.CharField(max_length=100, null=False)
    disaster_state = models.CharField(max_length=100, null=False)
    disaster_country = models.CharField(max_length=100, null=False)
    disaster_type = models.CharField(max_length=50, null=False)
    disaster_description = models.TextField(max_length=300, null=False)
    disaster_comments = models.TextField(max_length=300, null=False)
    tif_middle_latitude = models.FloatField(null=False)
    tif_middle_longitude = models.FloatField(null=False)
    pre_tif_path = models.CharField(max_length=300, null=False)
    post_tif_path = models.CharField(max_length=300, null=False)
    results = models.JSONField(default=dict, null=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"InferenceModel - {self.id} (User: {self.user.username}, Created At: {self.created_at}, Disaster Type: {self.disaster_type}, City: {self.disaster_city}, Country: {self.disaster_country})"


class LoginHistoryModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Login: {self.login_time}, Logout: {self.logout_time}"