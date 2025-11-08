"""Authentication service."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from ticketer.core.config import settings
from ticketer.models.user import User
from ticketer.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for user authentication."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int) -> str:
        """Create a JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def register_user(self, email: str, password: str) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        hashed_password = self.hash_password(password)
        return self.user_repo.create(email=email, hashed_password=hashed_password)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

