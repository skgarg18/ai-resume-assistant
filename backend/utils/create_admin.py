import secrets
import string


from auth.security import hash_password
from database.active_repository import user_repo


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

    try:
        email = input("Enter email: ").strip().lower()

        if not email:
            print("Email cannot be empty.")
            return

        existing_user = user_repo.get_user_by_email(email)

        if existing_user:
            print("User with this email already exists.")
            return

        password = generate_password()

        user = user_repo.create_user(
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True
        )

        if not user:
            print("Error in creating user")
            return

        print("\nUser created successfully!")
        print(f"Email    : {email}")
        print(f"Password : {password}")

    except Exception as e:
        print(f"An error occurred {e}")

if __name__ == "__main__":
    create_user()