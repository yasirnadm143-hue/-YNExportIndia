from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "price", "image"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name",
            "first_name",
            "last_name",
            "father_name",
            "mobile",
            "pincode",
            "landmark",
            "district",
            "state",
            "country",
            "address",
        ]
