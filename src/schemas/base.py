from pydantic import BaseModel, Field

from src.database import models


class UserInfo(BaseModel):
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User Name")
    username: str = Field(..., description="User Account Username")

    @staticmethod
    def from_model(user: models.User) -> "UserInfo":
        return UserInfo(id=user.id, name=user.name, username=user.account[0].username)
