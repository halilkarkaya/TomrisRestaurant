import getpass
import os

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q


class Command(BaseCommand):
    help = (
        "tomris yonetici hesabini olusturur veya gunceller ve diger tum "
        "yonetici hesaplarini siler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password-env",
            default="TOMRIS_ADMIN_PASSWORD",
            help=(
                "Sifreyi okuyacak ortam degiskeni "
                "(varsayilan: TOMRIS_ADMIN_PASSWORD)."
            ),
        )

    def handle(self, *args, **options):
        username = "tomris"
        password = os.getenv(options["password_env"])

        if not password:
            password = getpass.getpass("tomris icin yeni admin sifresi: ")
            confirmation = getpass.getpass("Yeni admin sifresi (tekrar): ")
            if password != confirmation:
                raise CommandError("Girilen sifreler ayni degil; hicbir hesap degistirilmedi.")

        User = get_user_model()
        validation_user = User(**{User.USERNAME_FIELD: username})
        try:
            password_validation.validate_password(password, validation_user)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc

        username_lookup = {User.USERNAME_FIELD: username}
        with transaction.atomic():
            user, created = User.objects.get_or_create(**username_lookup)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()

            other_admins = User.objects.filter(
                Q(is_staff=True) | Q(is_superuser=True)
            ).exclude(pk=user.pk)
            deleted_admin_count = other_admins.count()
            other_admins.delete()

        action = "olusturuldu" if created else "guncellendi"
        self.stdout.write(
            self.style.SUCCESS(
                f"'{username}' hesabi {action}; diger yoneticilere ait "
                f"{deleted_admin_count} kullanici hesabi silindi."
            )
        )
