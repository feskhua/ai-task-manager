import re
from typing_extensions import Annotated

from pydantic import SecretStr, BeforeValidator
from sqlmodel import SQLModel


def validate_password(value):
    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{3,20}$"

    pat = re.compile(reg)

    mat = re.search(pat, value)

    if not mat:
        raise ValueError(
            """
            Allowed characters in the password:
            - Uppercase letters (A-Z) — at least one required
            - Lowercase letters (a-z) — at least one required
            - Digits (0-9) — at least one required
            - Special characters (@$!%*#?&) — at least one required
            - Length: 3 to 20 characters
            - No spaces or other special characters are allowed
            """
        )

    return value

ValidPassword = Annotated[SecretStr, BeforeValidator(validate_password)]


class User(SQLModel):
    """Base model for user-related operations containing common fields."""
    username: str
    email: str | None = None


class UserCreate(User):
    """
    Model for creating a new user.

    Attributes:
        password: Required password for the new user
    """
    password: ValidPassword


class UserRead(User):
    """
    Model for reading basic user information.

    Attributes:
        id: Unique identifier of the user
    """
    id: int


class UserDetail(User):
    """
    Model for retrieving detailed user information including password.

    Attributes:
        id: Unique identifier of the user
        password: User's password
    """
    id: int
    password: SecretStr


class UserPasswordUpdate(SQLModel):
    """
    A model for updating a user's password with validation.

    Attributes:
        password (ValidPassword): The new password meeting validation requirements.
        old_password (SecretStr): The current password for verification, stored securely.
    """
    password: ValidPassword
    old_password: SecretStr


class UserMessage(SQLModel):
    message: str
