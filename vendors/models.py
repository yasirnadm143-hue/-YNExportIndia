from django.db import models
from django.conf import settings

class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    gst_number = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name
