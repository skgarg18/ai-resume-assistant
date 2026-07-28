import secrets
import string

from auth.security import hash_password
from database.active_repository import user_repo
from utils.log_utils import bind_logger


logger = bind_logger(component="create_user")


def generate_password(length: int = 12) -> str:
    """
    Generate a secure random password.
    """
    alphabet = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*"
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


def create_user():
    """
    Create an admin user from the command line.
    """

    try:

        email = input("Enter email: ").strip().lower()

        if not email:
            logger.error("Email cannot be empty.")
            return

        logger.info(
            "Checking whether user already exists | email={}",
            email,
        )

        existing_user = user_repo.get_user_by_email(email)

        if existing_user:
            logger.warning(
                "User already exists | email={}",
                email,
            )
            return

        password = generate_password()

        logger.info(
            "Creating admin user | email={}",
            email,
        )

        user = user_repo.create_user(
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )

        if not user:
            logger.error(
                "Failed to create user | email={}",
                email,
            )
            return

        logger.info(
            "User created successfully | email={}",
            email,
        )

        print("\nUser created successfully!")
        print(f"Email    : {email}")
        print(f"Password : {password}")

    except Exception:
        logger.exception(
            "Unexpected error while creating user"
        )


if __name__ == "__main__":
    create_user()