from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
import hashlib
from .config import settings

#  Password hashing with bcrypt - FIXED
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  
)


class SecurityService:
    @staticmethod
    def _prepare_password(password: str) -> bytes:
        """
        Prepare password for bcrypt (max 72 bytes)
        Uses SHA256 to hash long passwords first
        """
        if len(password.encode('utf-8')) > 72:
            # Hash long passwords with SHA256 first
            return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')
        return password.encode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Prepare password (handle long passwords)
            prepared = SecurityService._prepare_password(plain_password)
            return pwd_context.verify(prepared, hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        try:
            # Prepare password (handle long passwords)
            prepared = SecurityService._prepare_password(password)
            return pwd_context.hash(prepared)
        except Exception as e:
            print(f"Password hashing error: {e}")
            raise ValueError(f"Failed to hash password: {str(e)}")
    
    @staticmethod
    def create_access_token(
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None,
        extra_claims: dict = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access"
        }
        
        if extra_claims:
            to_encode.update(extra_claims)
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        subject: Union[str, Any],
        extra_claims: dict = None
    ) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh"
        }
        
        if extra_claims:
            to_encode.update(extra_claims)
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Generate a secure random password"""
        if length > 64:
            length = 64  # Limit to safe length
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)


security_service = SecurityService()