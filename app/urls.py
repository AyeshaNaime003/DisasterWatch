from django.urls import path
from django.conf.urls import handler404
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('map/', views.map, name="map"),
    path('admin-panel/', views.adminPanel, name="admin-panel"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    path('update-profile/', views.profile, name="update-profile"),
    path('help/', views.help, name="help"),
    path('inferenceform/', views.inferenceform, name="inferenceform"),
    # path('<path:not_found>', TemplateView.as_view(template_name='app/404.html'), name='not_found'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
