from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('map/', views.map, name="map"),
    path('admin-panel/', views.adminPanel, name="admin-panel"),
    path('dashboard/', views.dashboard, name="dashboard"),
]
