from django.urls import path
from django.conf.urls import handler404
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('map/', views.map, name="map"),
    path('admin-panel/', views.adminPanel, name="admin-panel"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    path('update-profile/', views.profile, name="update-profile"),
    path('notifications/', views.notifications, name="notifications"),
    path('help/', views.help, name="help"),
    path('inferenceform/', views.inferenceform, name="inferenceform"),
]
handler404 = 'app.views.custom_404_view'
