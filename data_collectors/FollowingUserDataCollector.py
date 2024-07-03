from instagrapi.types import User

from base.base import Base
from session_manager.Session_Manager import SessionManager
from MD_Manager.MDManager import MDManager


class FollowingUserData(Base):
  def __init__(self, user_id: str = None, user_name: str = None, force_update: bool = False, **kwargs):
    self.sm = SessionManager()
    self.user_id = user_id
    self.user_name = user_name
    self.force_update = force_update
    self.client = self.sm.active_session
    if user_id is None and user_name is None:
      raise ValueError("Both user_id and user_name are empty")
    if user_id is None and user_name is not None:
      self.user_id = self.client.user_id_from_username(username=user_name)     # get username
    self.md = MDManager(user_id=self.user_id)
    self.kwargs = kwargs
    self._mode = self.__class__.__name__

  def collect(self) -> dict:
    if self.md.cache_exists and self.force_update is False:
      data = self.md.fetch_cache(mode=self._mode)
      if data:
        return data

    data = {}
    following_users: dict = self.client.user_following(user_id=self.user_id)
    for user in following_users:
      _user: User = following_users.get(user)
      _basic_user_data = self.md.serializer(obj=_user)
      if _user.is_private is False:
        _detailed_user_data = self.md.serializer(obj=self.client.user_info(user_id=_user.pk))
        data.update({_user.pk: _detailed_user_data})
        continue
      data.update({_user.pk: _basic_user_data})
    self.md.update(item=data, mode=self._mode)
    return data


if __name__ == '__main__':
  import time
  start = time.time()
  FollowingUserData(user_name='_the_hindutva__', force_update=True).collect()
  print("#########################", time.time() - start)
