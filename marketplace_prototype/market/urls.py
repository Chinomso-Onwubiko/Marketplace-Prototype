from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inquire/', views.inquire, name='inquire_cart'),
    path('inquire/<int:product_id>/', views.inquire, name='inquire'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('farmer/login/', views.farmer_login, name='farmer_login'),
    path('farmer/logout/', views.farmer_logout, name='farmer_logout'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/inquiries/<int:inquiry_id>/respond/', views.respond_to_inquiry, name='respond_to_inquiry'),
    path('farmer/inquiries/<int:inquiry_id>/status/', views.update_inquiry_status, name='update_inquiry_status'),
]