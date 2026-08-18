from pydantic import BaseModel


class Profile(BaseModel):
    user_id: int
    username: str
    bio: str | None = None
