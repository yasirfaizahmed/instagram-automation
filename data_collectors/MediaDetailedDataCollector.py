import time
from instagrapi.utils import random_delay
from os.path import join, exists
from os import mkdir
import json
from typing import List
from instagrapi.types import Media
import datetime
from attributedict.collections import AttributeDict

from base.base import Base
from session_manager.Session_Manager import SessionManager
from MD_Manager.MDManager import MDManager
from data_collectors.MediaDataCollector import MediaData


class MediaDataDetailed(Base):
  def __init__(self, user_id: str = None, user_name: str = None, force_update: bool = False,
               **kwargs):
    self.sm = SessionManager()
    self.user_id = user_id
    self.user_name = user_name
    self.force_update = force_update
    self.client = self.sm.active_session
    if user_id is None and user_name is None:
      raise ValueError("Both user_id and user_name are empty")
    if user_id is None and user_name is not None:
      self.user_id = self.client.user_id_from_username(username=user_name)     # get username
    self.user_info = self.client.user_info(user_id=self.user_id)
    # self.md = MDManager(user_id=self.user_id)
    self.kwargs = kwargs
    self._mode = self.__class__.__name__
    self._generate_cache_path()

  def _generate_cache_path(self):
    self.user_dir = join("MD", (self.user_name or self.user_id))
    if exists(self.user_dir) is False:
      mkdir(self.user_dir)
    self.cache_file = join(self.user_dir, self._mode + '.json')
    if exists(self.cache_file) is False:
      open(self.cache_file, 'w').close()

  def serialize(self, obj):
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

  def collect(self):
    if exists(self.cache_file) is False or self.force_update:
      data = {}
      self.logger.info("Starting to collect user media data, this will take a while...")
      medias: List[Media] = MediaData(user_name=self.user_name, force_update=False).collect()
      i = 1
      for media in medias:
        self.logger.info("collecting data for media index: {}, with {} comments".format(i, media.comment_count))
        _media_data = self.serialize(obj=media)
        comments = self.client.media_comments_chunk(media_id=media.id,
                                                    max_amount=5000)[0]
        comment_data = {}
        for comment in comments:
          _comment_data = self.serialize(obj=comment)
          comment_data.update({comment.pk: _comment_data})
        final_data = {media.id: {'media': _media_data, 'comments': comment_data}}
        data.update(final_data)
        i += 1
        # saving to file for very media iteration
        fp = open(self.cache_file, 'w')
        json.dump(data, fp)
        self.logger.info("Dumped MediaData of user {} in file {}".format((self.user_name or self.user_id),
                                                                         self.cache_file))
      return data
    else:
      fp = open(self.cache_file, 'r')
      serialized_data = json.load(fp)
      return serialized_data


if __name__ == '__main__':
  start = time.time()
  MediaDataDetailed(user_name='opindia_com', force_update=True).collect()
  print("#########################", time.time() - start)
