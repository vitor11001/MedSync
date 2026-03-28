from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class EnsureDefaultSuperuserCommandTests(TestCase):
    """Tests for the default superuser bootstrap command."""

    def test_creates_default_superuser_when_none_exists(self):
        """The command should create the default superuser when absent."""
        stdout = StringIO()

        with patch.dict(
            "os.environ",
            {
                "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
                "DJANGO_SUPERUSER_PASSWORD": "admin123",
                "DJANGO_SUPERUSER_FIRST_NAME": "Admin",
                "DJANGO_SUPERUSER_LAST_NAME": "User",
            },
            clear=False,
        ):
            call_command("ensure_default_superuser", stdout=stdout)

        user_model = get_user_model()
        self.assertEqual(user_model.objects.filter(is_superuser=True).count(), 1)

        superuser = user_model.objects.get(email="admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.first_name, "Admin")
        self.assertEqual(superuser.last_name, "User")
        self.assertIn("Default superuser created", stdout.getvalue())

    def test_does_not_create_another_superuser_when_one_already_exists(self):
        """The command should be idempotent once a superuser exists."""
        user_model = get_user_model()
        user_model.objects.create_superuser(
            email="owner@example.com",
            password="secret123",
        )

        stdout = StringIO()
        call_command("ensure_default_superuser", stdout=stdout)

        self.assertEqual(user_model.objects.filter(is_superuser=True).count(), 1)
        self.assertFalse(user_model.objects.filter(email="admin@example.com").exists())
        self.assertIn("A superuser already exists", stdout.getvalue())
