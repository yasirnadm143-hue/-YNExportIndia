from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Product

class CustomUserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    mobile_number = forms.CharField(max_length=15, required=True, label="Mobile Number")
    pan_card = forms.CharField(max_length=20, required=True, label="PAN Card")
    aadhaar_card = forms.CharField(max_length=20, required=True, label="Aadhaar Card")
    upline_username = forms.CharField(required=False, label="Upline ID (Username)")
    profile_picture = forms.ImageField(required=False, label="Profile Picture")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'mobile_number', 'pan_card', 'aadhaar_card', 'profile_picture'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.mobile_number = self.cleaned_data['mobile_number']
        user.pan_card = self.cleaned_data['pan_card']
        user.aadhaar_card = self.cleaned_data['aadhaar_card']
        
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']

        upline_uname = self.cleaned_data.get('upline_username')
        if upline_uname:
            try:
                upline_user = CustomUser.objects.get(username=upline_uname)
                user.upline = upline_user
            except CustomUser.DoesNotExist:
                pass

        if commit:
            user.save()
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
