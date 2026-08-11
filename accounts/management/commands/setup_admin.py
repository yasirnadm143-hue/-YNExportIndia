import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create the YN Export India admin account only if it does not exist"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_ADMIN_USERNAME or DJANGO_ADMIN_PASSWORD not set. "
                    "Skipping admin setup."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            # IMPORTANT:
            # Never overwrite an existing admin password on startup.
            changed = False

            if not user.is_active:
                user.is_active = True
                changed = True

            if not user.is_staff:
                user.is_staff = True
                changed = True

            if not user.is_superuser:
                user.is_superuser = True
                changed = True

            if changed:
                user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin already exists: {username}. Password unchanged."
                )
            )
            return

        user = User(
            username=username,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin account created: {username}"
            )
        )
