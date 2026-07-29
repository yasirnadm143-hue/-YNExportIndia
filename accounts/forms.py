from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product


class CustomUserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    mobile_number = forms.CharField(max_length=15, required=True)

    pan_card = forms.CharField(max_length=20, required=True)

    aadhaar_card = forms.CharField(max_length=20, required=True)

    referral_id = forms.CharField(
        max_length=20,
        required=False,
        label="Referral ID"
    )

    profile_picture = forms.ImageField(
        required=False
    )

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "pan_card",
            "aadhaar_card",
            "referral_id",
            "profile_picture",
            "password1",
            "password2",
        )
    def save(self, commit=True):

        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.mobile_number = self.cleaned_data["mobile_number"]
        user.pan_card = self.cleaned_data["pan_card"]
        user.aadhaar_card = self.cleaned_data["aadhaar_card"]

        if self.cleaned_data.get("profile_picture"):
            user.profile_picture = self.cleaned_data["profile_picture"]

        ref = self.cleaned_data.get("referral_id")

        if ref:
            try:
                upline = CustomUser.objects.get(
                    referral_id=ref
                )
                user.upline = upline
            except CustomUser.DoesNotExist:
                pass

        if commit:
            user.save()

        return user


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "title",
            "description",
            "price",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }
