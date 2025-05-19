from pydantic import BaseModel, EmailStr
from typing import Literal, Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Literal["recruiter", "job_seeker"]  # Restrict to valid roles


class UserLogin(BaseModel):
    email: str
    password: str
