import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "Create or update the deployment administrator from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Admin creation skipped: ADMIN_USERNAME, ADMIN_EMAIL, "
                    "and ADMIN_PASSWORD must all be set."
                )
            )
            return

        user_model = get_user_model()
        field_names = {field.name for field in user_model._meta.get_fields()}
        login_field = user_model.USERNAME_FIELD

        lookup = Q()
        if login_field == "email" and "email" in field_names:
            lookup |= Q(email=email)
        elif login_field == "username" and "username" in field_names:
            lookup |= Q(username=username)
        elif login_field in field_names:
            lookup |= Q(**{login_field: email})

        if "email" in field_names:
            lookup |= Q(email=email)
        if "username" in field_names:
            lookup |= Q(username=username)

        user = user_model.objects.filter(lookup).first()
        if user is None:
            user = user_model()

        if "email" in field_names:
            user.email = email
        if "username" in field_names:
            user.username = username
        if login_field in field_names and login_field not in {"email", "username"}:
            setattr(user, login_field, email)
        if "is_staff" in field_names:
            user.is_staff = True
        if "is_superuser" in field_names:
            user.is_superuser = True
        if "is_active" in field_names:
            user.is_active = True
        if "role" in field_names:
            user.role = "admin"

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Admin account created or updated successfully."
            )
        )