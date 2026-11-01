import os

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Ensure the configured site administrator exists."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "campus-admin")
        email = os.environ.get("ADMIN_EMAIL", "")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username:
            raise CommandError("ADMIN_USERNAME must not be empty.")
        if not password:
            raise CommandError(
                "ADMIN_PASSWORD must be set to a strong secret in the environment."
            )

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user:
            if not user.is_superuser:
                raise CommandError(
                    f"The configured administrator username {username!r} "
                    "already belongs to a non-superuser account."
                )
            self.stdout.write(f"Administrator {username!r} already exists.")
            return

        candidate = User(username=username, email=email)
        try:
            password_validation.validate_password(password, user=candidate)
        except ValidationError as error:
            raise CommandError(
                "ADMIN_PASSWORD does not meet the configured password policy: "
                + "; ".join(error.messages)
            ) from error

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(f"Created administrator {username!r}.")
