from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),
    path('settings/', views.user_settings, name='user_settings'),
    path('wallet/', views.wallet_view, name='wallet_view'),
    path('support/', views.customer_support, name='customer_support'),
    path('notifications/', views.notifications_view, name='notifications'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_step1, name='register'),
    path('register/verify-otp/', views.register_verify_otp, name='register_verify_otp'),
    path('register/complete/', views.register_complete, name='register_complete'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('order/<int:pk>/', views.order_product, name='order_product'),

    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('my-orders/', views.my_orders, name='my_orders'),

    path('upload-product/', views.upload_product, name='upload_product'),

    # Product Edit/Delete
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
]
