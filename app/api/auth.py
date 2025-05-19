from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.models.document_models import User  # adjust if models folder changed
from app.schemas.auth_schema import UserCreate, UserLogin
from app.utils.auth_utils import get_password_hash, verify_password
from fastapi.responses import JSONResponse
from app.utils.jwt_utils import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation error"},
    },
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    # Check if a user with the same username already exists
    existing_user = await User.find_one(User.email == user.email)
    if existing_user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Email already exists"},
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
    )
    await new_user.insert()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully"},
    )


@router.post("/login")
async def login(user: UserLogin):
    db_user = await User.find_one(User.email == user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid credentials"},
        )
    access_token = create_access_token(
        {"sub": str(db_user.id)}
    )  # Convert PydanticObjectId to string
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"access_token": access_token, "token_type": "bearer"},
    )
