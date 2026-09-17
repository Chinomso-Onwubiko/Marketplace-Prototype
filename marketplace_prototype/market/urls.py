from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inquire/<int:product_id>/', views.inquire, name='inquire'),
    path('farmer/login/', views.farmer_login, name='farmer_login'),
    path('farmer/logout/', views.farmer_logout, name='farmer_logout'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
]