from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    # path('map/', views.map, name="map"),
    path('map/<int:inference_id>/', views.map_with_id, name="map_with_id"),
    # path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard/<int:inference_id>/', views.dashboard_with_id, name="dashboard_with_id"),
    path('profile/', views.profile, name="profile"),
    path('update-profile/', views.profile, name="update-profile"),
    path('help/', views.help, name="help"),
    path('inferenceform/', views.inferenceform, name="inferenceform"),
    path('admin-panel/', views.adminPanel, name="admin-panel"),
    path('add-user/', views.addUser, name="add-user"),
    path('edit-user/<int:user_id>/', views.edit_user, name="edit-user"),
    path('delete-user/<int:user_id>/', views.delete_user, name="delete-user"),
    path('get-user-details/<int:user_id>/', views.get_user_details, name='get-user-details'),
]