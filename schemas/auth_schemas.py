from sqlmodel import SQLModel


class Token(SQLModel):
    """
    Model representing an authentication token response.

    Attributes:
        access_token: The JWT access token string
        token_type: The type of token (e.g., "bearer")
    """
    access_token: str
    token_type: str

class TokenData(SQLModel):
    """
    Model representing the data contained within a token.

    Attributes:
        user_id: Optional user identifier associated with the token
    """
    user_id: int | None = None
