from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager as BUM  # noqa: N817
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import BaseModel


class BaseUserManager(BUM):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, password, **extra_fields)


class BaseUser(BaseModel):
    class Meta:
        verbose_name: str = "User"
        verbose_name_plural: str = "Users"


class Member(BaseUser, AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        _("email address"),
        blank=False,
        max_length=255,
        unique=True,
        help_text=_("Enter the email address of the employee."),
    )
    phone_number = models.PositiveBigIntegerField(
        _("phone number"),
        unique=True,
        help_text=_("Enter the phone number of the employee."),
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    class Meta:
        verbose_name: str = "Member"
        verbose_name_plural: str = "Members"

    def __str__(self) -> str:
        return f"{self.full_name} - {self.email}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
