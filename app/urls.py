from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('map/', views.map, name="map"),
    path('admin-panel/', views.adminPanel, name="admin-panel"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    path('notifications/', views.notifications, name="notifications"),
    path('help/', views.help, name="help"),
    path('settings/', views.settings, name="settings"),
]
