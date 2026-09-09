from django.urls import path
from . import views

urlpatterns = [

    path("seller/register/", views.seller_register_view, name="seller_register"),
    path("seller/pending/", views.seller_pending_view, name="seller_pending"),

    path("admin-setup/", views.one_time_admin_setup, name="one_time_admin_setup"),
    path('', views.home_view, name='home'),

    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('mlm-commission/', views.mlm_commission_view, name='mlm_commission'),
    path(
        'mlm-commission/download/',
        views.download_commission_csv,
        name='download_commission_csv',
    ),
    path('my-network/', views.mlm_tree_view, name='mlm_tree'),
    path(
        'mlm-commission-history/',
        views.mlm_commission_history_view,
        name='mlm_commission_history',
    ),
    path(
        'direct-team/',
        views.direct_team_view,
        name='direct_team',
    ),
    path(
        'total-team/',
        views.total_team_view,
        name='total_team',
    ),

    path('profile/', views.user_profile, name='profile'),
    path('settings/', views.user_settings, name='user_settings'),
    path('bonus_balance/', views.bonus_balance_view, name='bonus_balance_view'),
    path('support/', views.customer_support, name='customer_support'),
    path('support/<str:ticket_id>/', views.support_ticket_detail, name='support_ticket_detail'),
    path('notifications/', views.notifications_view, name='notifications'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_step1, name='register'),
    path('register/verify-otp/', views.register_verify_otp, name='register_verify_otp'),
    path('register/complete/', views.register_complete, name='register_complete'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    path('order/<int:pk>/', views.order_product, name='order_product'),

    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),

    path("seller/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/products/", views.seller_products, name="seller_products"),
    path("seller/orders/", views.seller_orders, name="seller_orders"),
    path("seller/bonus_balance/", views.bonus_balance_view, name="bonus_balance"),
    path("seller/orders/<int:order_id>/accept/", views.seller_accept_order, name="seller_accept_order"),
    path("seller/orders/<int:order_id>/pack/", views.seller_pack_order, name="seller_pack_order"),
    path("seller/orders/<int:order_id>/label/download/", views.seller_download_label, name="seller_download_label"),
    path("seller/orders/<int:order_id>/label/generate/", views.seller_generate_label, name="seller_generate_label"),
    path("seller/orders/<int:order_id>/ship/", views.seller_ship_order, name="seller_ship_order"),
    path("seller/orders/<int:order_id>/deliver/", views.seller_deliver_order, name="seller_deliver_order"),
    path("seller/products/add/", views.seller_add_product, name="seller_add_product"),

    path('upload-product/', views.upload_product, name='upload_product'),

    # Product Edit/Delete
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path(
        "invoice/<int:order_id>/",
        views.download_invoice,
        name="download_invoice",
    ),
]
