from beanie import Document
from typing import List, Optional
from datetime import datetime
from pydantic import Field


class User(Document):
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"


class Interview(Document):
    title: str
    description: Optional[str] = None
    user_id: str
    questions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "interviews"


class Resume(Document):
    user_id: str
    file_name: str
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "resumes"


# Add all document models to this list to register them with Beanie
document_models = [User, Interview, Resume]
