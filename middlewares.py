import jwt
import datetime
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from settings import settings
SECRET_KEY = settings.SECRET_KEY # Change this to a secure secret key
ALGORITHM = "HS256"

# Function to generate a JWT token
def create_jwt_token(data: dict, expires_delta: int = 60):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to verify a JWT token
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Middleware (Dependency) for Protected Routes
security = HTTPBearer()

def jwt_auth_required(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    return verify_jwt_token(token)
