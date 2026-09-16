from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inquire/<int:product_id>/', views.inquire, name='inquire'),
]