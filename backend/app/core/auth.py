import requests
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from functools import lru_cache

bearer_scheme = HTTPBearer()

@lru_cache()
def get_jwks():
    resp = requests.get(settings.COGNITO_JWKS_URL)
    resp.raise_for_status()
    return resp.json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    jwks = get_jwks()
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(token, public_key, algorithms=[unverified_header["alg"]], audience=settings.COGNITO_CLIENT_ID)
        return {"sub": payload["sub"], "email": payload.get("email"), "role": payload.get("custom:role", "student")}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
