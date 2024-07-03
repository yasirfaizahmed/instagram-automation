import json
from os import (mkdir, walk, listdir)
from os.path import (exists, join)
from typing import Literal
import datetime
import time
from threading import Thread

from base.base import Base
# from MD_Manager.MDConfig import comment, media, user
from patterns.Patterns import Singleton


MD_DIR = "MD"


class MDManager(Base, metaclass=Singleton):
  def __init__(self, user_id: str, **kwargs):
    self.user_id = user_id
    self.user_dir = join(MD_DIR, user_id)
    self._cache_exists = False
    self._autosave_thread: Thread = None
    self._autosave_timeout = 5 * 60   # seconds
    self.autosave_data: dict = None
    if exists(self.user_dir):
      self.logger.info("User dir already exists, containing: {}".format(listdir(self.user_dir)))
      self._cache_exists = True

    if not exists(MD_DIR):
      self.logger.warning("No MedaData dir was found, creating new one")
      mkdir(MD_DIR)   # parent
    if not exists(self.user_dir):
      self.logger.info("User Dir not found, creating new one")
      mkdir(self.user_dir)    # user dir

  @property
  def cache_exists(self):
    return self._cache_exists

  def change_mode(self, mode: Literal["medias", "comments"]):
    self.MD_path = join(MD_DIR, mode, (self.user_id or self.media_id)) + '.json'    # MD file

  def check_local(self, id: str):
    for dirpath, dir, file in walk(MD_DIR):
      for f in file:
        if f.split('.')[0] == id:
          self.logger.info("Found data for id {} locally under {}".format(id, dirpath))
          fp = open(join(dirpath, file), 'r')
          return json.load(fp)
    return False

  def serializer(self, obj):
    if isinstance(obj, dict):
      return obj
    new_dict = {}
    for attr in obj.__dict__:
      attribute = getattr(obj, attr, None)
      if attribute is not None and isinstance(attribute, datetime.datetime):
        new_dict.update({attr: attribute.strftime('%d-%m-%Y %H:%M:%S')})
      if isinstance(attribute, (int, str, float)):
        new_dict.update({attr: attribute})
    return new_dict

  def fetch_cache(self, mode: str):
    file_to_fetch = join(self.user_dir, mode + '.json')
    if exists(file_to_fetch):
      fp = open(file_to_fetch, 'r')
      return json.load(fp)
    return False

  def update(self, item: dict, mode: Literal["MediaData", "FollowingUserData"]):
    if isinstance(item, dict) is False:
      raise TypeError("item passed is not of type dictonary")

    MD_path = join(self.user_dir, mode + '.json')
    fp = open(MD_path, 'w', encoding='utf-8')
    json.dump(item, fp, ensure_ascii=False)    # update the file
    self.logger.info("Updating the file {}".format(MD_path))
    return True

  def _autosave_thread_target(self):
    start_time = time.time()
    while True:
      current_time = time.time()
      if (current_time - start_time) > self._autosave_timeout:
        pass

  def autosave(self):
    self._autosave_thread = Thread(target=self._autosave_thread_target, args=[])
    self._autosave_thread.start()


if __name__ == '__main__':
  md = MDManager(mode="medias", user_id='1234')
