import logging
from typing import Dict, Any

from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from fastapi import HTTPException, status
from requests.exceptions import RequestException, Timeout

from core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()


async def verify_google_token(code: str) -> Dict[str, Any]:
    """
    Verify the Google OAuth token and return the authenticated user information.

    Args:
        code: The authorization code received from Google OAuth

    Returns:
        Dict containing verified user information

    Raises:
        HTTPException: If authentication fails for any reason
    """
    if not code or not isinstance(code, str):
        logger.error("Invalid authorization code format")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="INVALID_AUTHORIZATION_CODE"
        )

    try:
        # Configure OAuth flow with client details and required scopes
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        }

        # Set up the OAuth flow
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=[
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "openid",
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

        # Exchange authorization code for tokens
        try:
            flow.fetch_token(code=code)
        except Exception as e:
            logger.error(f"Failed to fetch token from Google: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="INVALID_AUTHORIZATION_CODE",
            )

        # Validate credentials and ID token
        if not flow.credentials:
            logger.error("No credentials received from Google")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="AUTHENTICATION_FAILED"
            )

        id_token_str = flow.credentials.id_token
        if not id_token_str:
            logger.error("No ID token in Google credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="NO_ID_TOKEN_RECEIVED"
            )

        # Verify the ID token
        client = requests.Request()
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                client,
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60,  # Allow 1 minute clock skew for server time differences
            )
        except ValueError as e:
            logger.error(f"Token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN"
            )

        # Check for required fields in the token payload
        if not idinfo.get("email"):
            logger.warning("Email missing from verified token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="EMAIL_REQUIRED"
            )

        # Check if email is verified (Google best practice)
        if not idinfo.get("email_verified", False):
            logger.warning(f"Unverified email: {idinfo.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="EMAIL_NOT_VERIFIED"
            )

        # Everything passed, return the verified user info
        logger.info(f"Successfully authenticated Google user: {idinfo.get('email')}")
        return idinfo

    except Timeout:
        logger.error("Google authentication request timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AUTHENTICATION_TIMEOUT"
        )
    except RequestException as e:
        logger.error(f"Network error during Google authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AUTHENTICATION_SERVICE_UNAVAILABLE",
        )
    except GoogleAuthError as e:
        logger.error(f"Google auth library error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTHENTICATION_ERROR",
        )
    except Exception as e:
        logger.exception(f"Unexpected error during Google authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR",
        )
