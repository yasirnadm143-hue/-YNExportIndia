from django import forms
from django.contrib.auth import get_user_model
from .models import Product, Order

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create password"
        }),
        label="Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm password"
        }),
        label="Confirm Password"
    )

    referral_id = forms.CharField(
        required=False,
        label="Referral ID (Optional)",
        widget=forms.TextInput(attrs={
            "placeholder": "Example: YN123456"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "referral_id",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Enter username"
            }),
            "first_name": forms.TextInput(attrs={
                "placeholder": "Enter first name"
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Enter last name"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Enter email address"
            }),
            "phone_number": forms.TextInput(attrs={
                "placeholder": "Enter mobile number"
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()

        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError(
                "This mobile number is already registered."
            )

        return phone

    def clean_referral_id(self):
        referral_id = self.cleaned_data.get("referral_id", "").strip()

        if referral_id:
            if not User.objects.filter(referral_id=referral_id).exists():
                raise forms.ValidationError(
                    "Invalid Referral ID."
                )

        return referral_id

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data["password"]
        referral_id = self.cleaned_data.get("referral_id")

        user.set_password(password)

        # Set upline from Referral ID
        if referral_id:
            try:
                upline_user = User.objects.get(
                    referral_id=referral_id
                )
                user.upline = upline_user
            except User.DoesNotExist:
                user.upline = None

        if commit:
            user.save()

        return user


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
