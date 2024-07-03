from pydantic import BaseModel
from typing import Optional, List


class Comment(BaseModel):
  id: str
  text: str
  parent_id: Optional[str]
  user_id: str
  likes: Optional[int]


class Media(BaseModel):
  id: str
  caption: str
  user_id: str
  likes: Optional[int]
  comments: List[Comment]


class User(BaseModel):
  id: str
  username: str
  bio: str
  followers: int
  following: int
  medias: List[Media]
