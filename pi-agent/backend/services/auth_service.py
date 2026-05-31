"""手机号验证码登录相关服务。"""
from datetime import datetime, timedelta
from secrets import randbelow

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    ALGORITHM,
    APP_ENV,
    SECRET_KEY,
    SMS_CODE_TTL_SECONDS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_code_store: dict[str, tuple[str, datetime]] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, phone: str) -> str:
    expires_at = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def generate_sms_code(phone: str) -> str:
    code = f"{randbelow(1000000):06d}"
    expires_at = datetime.utcnow() + timedelta(seconds=SMS_CODE_TTL_SECONDS)
    _code_store[phone] = (code, expires_at)
    return code


def verify_sms_code(phone: str, code: str) -> bool:
    stored = _code_store.get(phone)
    if not stored:
        return False

    expected_code, expires_at = stored
    if datetime.utcnow() > expires_at:
        _code_store.pop(phone, None)
        return False

    is_match = expected_code == code
    if is_match:
        _code_store.pop(phone, None)
    return is_match


def get_send_code_debug_value(code: str) -> str | None:
    if APP_ENV.lower() in {"dev", "development", "local", "test"}:
        return code
    return None


def parse_token_subject(token: str) -> int:
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise ValueError("invalid_token") from exc

    sub = payload.get("sub")
    if sub is None:
        raise ValueError("invalid_token")

    try:
        return int(sub)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_token") from exc
