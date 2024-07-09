from typing import Optional

from .models import Member


def user_create(
    *,
    first_name: str,
    last_name: str,
    email: str,
    phone_number: str,
    is_active: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
    password: Optional[str] = None,
) -> Member:
    return (
        Member.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            password=password,
        ),
    )
