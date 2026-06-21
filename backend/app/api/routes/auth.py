from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from app.services import auth_service
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWT guard. Use as a FastAPI dependency on any protected route.
    Usage: current_user: dict = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/register", status_code=201)
async def register(data: RegisterRequest):
    """Register a new user."""
    try:
        user = await auth_service.register_user(
            email=data.email,
            password=data.password,
            name=data.name,
        )
        return {"message": "Account created successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(data: LoginRequest):
    """Login and get JWT token."""
    try:
        return await auth_service.login_user(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current logged in user. Tests if token is valid."""
    return current_user