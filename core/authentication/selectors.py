from core.users.models import Member


def user_get_login_data(*, current_user: Member):
    return {
        "id": getattr(current_user, "id", ""),
        "email": getattr(current_user, "email", ""),
        "first_name": getattr(current_user, "first_name", ""),
        "last_name": getattr(current_user, "last_name", ""),
        "full_name": getattr(current_user, "full_name", ""),
        "phone_number": getattr(current_user, "phone_number", ""),
        "is_staff": getattr(current_user, "is_staff", False),
    }
