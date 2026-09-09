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
        fields = [
            "category",
            "subcategory",
            "brand",
            "title",
            "description",
            "price",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Enter product name"
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Enter product description",
                "rows": 5,
            }),
            "price": forms.NumberInput(attrs={
                "placeholder": "Enter price",
                "step": "0.01",
                "min": "0",
            }),
        }


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


# ==========================
# SELLER REGISTRATION FORM
# ==========================

from django import forms
from .models import SellerProfile


class SellerRegistrationForm(forms.ModelForm):

    class Meta:
        model = SellerProfile

        fields = [
            "full_name",
            "email",
            "mobile",
            "age",
            "pan_number",
            "aadhaar_number",
            "pan_card",
            "aadhaar_card",
            "bank_account_number",
            "ifsc_code",
            "bank_account_name",
            "pickup_address",
            "pickup_pincode",
            "pickup_district",
            "pickup_state",
            "pickup_country",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Seller Full Name"
            }),

            "email": forms.EmailInput(attrs={
                "placeholder": "Seller Email"
            }),

            "mobile": forms.TextInput(attrs={
                "placeholder": "Mobile Number"
            }),

            "age": forms.NumberInput(attrs={
                "placeholder": "Age",
                "min": "18"
            }),

            "pan_number": forms.TextInput(attrs={
                "placeholder": "PAN Number",
                "maxlength": "10"
            }),

            "aadhaar_number": forms.TextInput(attrs={
                "placeholder": "Aadhaar Number",
                "maxlength": "12"
            }),

            "bank_account_number": forms.TextInput(attrs={
                "placeholder": "Bank Account Number"
            }),

            "ifsc_code": forms.TextInput(attrs={
                "placeholder": "IFSC Code"
            }),

            "bank_account_name": forms.TextInput(attrs={
                "placeholder": "Account Holder Name"
            }),

            "pickup_address": forms.Textarea(attrs={
                "placeholder": "Complete Pickup Address",
                "rows": 4
            }),

            "pickup_pincode": forms.TextInput(attrs={
                "placeholder": "Pickup Pincode"
            }),

            "pickup_district": forms.TextInput(attrs={
                "placeholder": "District"
            }),

            "pickup_state": forms.TextInput(attrs={
                "placeholder": "State"
            }),

            "pickup_country": forms.TextInput(attrs={
                "placeholder": "Country"
            }),
        }

    def clean_age(self):
        age = self.cleaned_data["age"]

        if age < 18:
            raise forms.ValidationError(
                "Seller की उम्र कम से कम 18 वर्ष होनी चाहिए।"
            )

        return age

    def clean_pan_number(self):
        pan = self.cleaned_data["pan_number"].strip().upper()

        if len(pan) != 10:
            raise forms.ValidationError(
                "PAN Number 10 characters का होना चाहिए।"
            )

        return pan

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data["aadhaar_number"].strip()

        if not aadhaar.isdigit() or len(aadhaar) != 12:
            raise forms.ValidationError(
                "Aadhaar Number 12 digits का होना चाहिए।"
            )

        return aadhaar

