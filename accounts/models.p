import random
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    referral_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    upline = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='downlines')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rank = models.CharField(max_length=50, default='Member')

    def save(self, *args, **kwargs):
        if not self.referral_id:
            # ऑटोमैटिक यूनीक रेफरल आईडी जनरेट करना
            self.referral_id = 'YN' + ''.join(random.choices('0123456789', k=6))
        super().save(*args, **kwargs)

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.title

