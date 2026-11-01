from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


@patch.dict(
    "os.environ",
    {
        "ADMIN_USERNAME": "campus-admin",
        "ADMIN_EMAIL": "admin@example.invalid",
        "ADMIN_PASSWORD": "A-strong-uncommon-password-2026!",
    },
)
class EnsureAdminUserTests(TestCase):
    def test_creates_configured_superuser(self):
        call_command("ensure_admin_user")

        admin = User.objects.get(username="campus-admin")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.check_password("A-strong-uncommon-password-2026!"))

    def test_existing_superuser_and_password_are_left_unchanged(self):
        admin = User.objects.create_superuser(
            username="campus-admin",
            email="admin@example.invalid",
            password="Original-strong-password-2026!",
        )

        call_command("ensure_admin_user")

        admin.refresh_from_db()
        self.assertTrue(admin.check_password("Original-strong-password-2026!"))
        self.assertFalse(admin.check_password("A-strong-uncommon-password-2026!"))
        self.assertEqual(User.objects.filter(username="campus-admin").count(), 1)

    def test_refuses_to_promote_existing_regular_user(self):
        User.objects.create_user(
            username="campus-admin",
            email="student@example.invalid",
            password="Student-password-2026!",
        )

        with self.assertRaisesMessage(CommandError, "non-superuser account"):
            call_command("ensure_admin_user")

        self.assertFalse(User.objects.get(username="campus-admin").is_superuser)

    def test_requires_password_environment_variable(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesMessage(CommandError, "ADMIN_PASSWORD must be set"):
                call_command("ensure_admin_user")
