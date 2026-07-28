from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_vendor, name="vendor_register"),
    path("dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
]
