from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import VendorForm
from .models import Vendor

@login_required
def register_vendor(request):
    if request.method == "POST":
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            return redirect("vendor_dashboard")
    else:
        form = VendorForm()

    return render(request, "vendors/register.html", {"form": form})

@login_required
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    return render(request, "vendors/dashboard.html", {"vendor": vendor})
