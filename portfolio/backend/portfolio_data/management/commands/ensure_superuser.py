from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from decouple import config


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables."

    def handle(self, *args, **options):
        username = config("DJANGO_SUPERUSER_USERNAME", default="mani")
        email = config("DJANGO_SUPERUSER_EMAIL", default="manigururam06@gmail.com")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="")

        if not password:
            password = get_random_secret_key()
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PASSWORD is not set. A random password was generated."
                )
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} superuser '{username}'."))
