from django import forms
from .models import Vendor

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            "company_name",
            "phone",
            "address",
            "gst_number",
        ]
