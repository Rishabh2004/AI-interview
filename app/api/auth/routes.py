from fastapi import APIRouter
from .utils import verify_google_token, generate_token_ids
from app.db.prisma import get_prisma
from .dtos import GoogleLoginRequest
from fastapi.responses import JSONResponse
from app.utils.jwt_utils import create_access_token, create_refresh_token

prisma = get_prisma()

auth = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        422: {"description": "Validation error"},
    },
)


@auth.post("/google")
async def google_login(body: GoogleLoginRequest):
    print(body.code)
    payload = await verify_google_token(body.code)

    # Check if user exists
    user = await prisma.user.find_unique(where={"email": payload["email"]})
    # Generate new token IDs
    token_ids = await generate_token_ids()
    # Generate JWT token

    if user:
        # Update existing user with new token IDs
        user = await prisma.user.update(
            where={"id": user.id},
            data={
                "accessTokenId": token_ids["access_token_id"],
                "refreshTokenId": token_ids["refresh_token_id"],
            },
        )
    else:
        # Create new user
        user = await prisma.user.create(
            data={
                "email": payload["email"],
                "name": payload.get("name"),
                "googleId": payload["sub"],
                "picture": payload.get("picture"),
                "accessTokenId": token_ids["access_token_id"],
                "refreshTokenId": token_ids["refresh_token_id"],
            }
        )
    access_token = create_access_token(
        user_id=user.id, access_token_id=token_ids["access_token_id"]
    )
    refresh_token = create_refresh_token(
        user_id=user.id, refresh_token_id=token_ids["refresh_token_id"]
    )
    return JSONResponse(
        status_code=200,
        content={
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "userId": user.id,
        },
    )
