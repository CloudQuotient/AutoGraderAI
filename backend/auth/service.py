from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import jwt
import requests
from functools import wraps

bearer_scheme = HTTPBearer()

# Cognito JWT verification

def get_jwks():
    resp = requests.get(settings.COGNITO_JWKS_URL)
    resp.raise_for_status()
    return resp.json()

def verify_jwt(token: str):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    payload = jwt.decode(token, public_key, algorithms=[unverified_header["alg"]], audience=settings.COGNITO_CLIENT_ID)
    return payload

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = verify_jwt(token)
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Role-based decorators

def student_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        if not user or user.get('custom:role') != 'student':
            raise HTTPException(status_code=403, detail='Student access required')
        return func(*args, **kwargs)
    return wrapper

def instructor_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        if not user or user.get('custom:role') != 'instructor':
            raise HTTPException(status_code=403, detail='Instructor access required')
        return func(*args, **kwargs)
    return wrapper

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        if not user or user.get('custom:role') != 'admin':
            raise HTTPException(status_code=403, detail='Admin access required')
        return func(*args, **kwargs)
    return wrapper
