import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the YN Export India admin account"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_ADMIN_USERNAME and DJANGO_ADMIN_PASSWORD "
                    "environment variables are required."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin account created: {username}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin account updated: {username}"
                )
            )
