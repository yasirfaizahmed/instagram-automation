# import math
# import time
import json
import csv
# from instagrapi.utils import random_delay
from os.path import join, exists
from os import mkdir
import datetime
from typing import List
from instagrapi.types import Media
from typing import Literal
from attributedict.collections import AttributeDict


from base.base import Base
from session_manager.Session_Manager import SessionManager


class MediaData(Base):
  def __init__(self, user_id: str = None, user_name: str = None, 
               force_update: bool = False,
               data_format: Literal["json", "csv"] = "csv",
               use_chunk=False, **kwargs):
    self.sm = SessionManager()
    self.user_id = user_id
    self.user_name = user_name
    self.data_format = data_format
    self.use_chunk = use_chunk
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
    self._field_names = ['pk', 'id', 'code', 'taken_at', 'media_type', 
                         'product_type', 'thumbnail_url', 'comment_count', 
                         'comments_disabled', 'commenting_disabled_for_viewer',
                         'like_count', 'caption_text', 'video_url', 'view_count',
                         'video_duration', 'title']

  def _generate_cache_path(self):
    if exists("MD") is False:
      mkdir("MD")
    self.user_dir = join("MD", (self.user_name or self.user_id))
    if exists(self.user_dir) is False:
      mkdir(self.user_dir)
    self.cache_file = join(self.user_dir, self._mode + '.json') if self.data_format == ".json" else join(self.user_dir, self._mode + '.csv')
    if exists(self.cache_file) is False:
      open(self.cache_file, 'w').close()
      return False
    else:   # cache file exists
      return True

  def update_csv(self, data: dict):
    fp = open(self.cache_file, 'w', newline='') if self.force_update else open(self.cache_file, 'w+', newline='')
    writer = csv.DictWriter(fp, fieldnames=self._field_names)
    if self.force_update:
      writer.writeheader()    # Write the header row
    for item in data.values():
      writer.writerow(item)

  def serialize(self, obj):
    if isinstance(obj, dict):
      return obj
    if isinstance(obj, list):   # list of objects
      new_dict = {}
      for item in obj:
        item_dict = {}
        for attr in item.__dict__:
          attribute = getattr(item, attr, None)
          if attribute is not None and isinstance(attribute, datetime.datetime):
            item_dict.update({attr: attribute.strftime('%d-%m-%Y %H:%M:%S')})
          if isinstance(attribute, (int, str, float)):
            item_dict.update({attr: attribute})
        new_dict.update({item.pk: item_dict})
      return new_dict
    new_dict = {}
    for attr in obj.__dict__:
      attribute = getattr(obj, attr, None)
      if attribute is not None and isinstance(attribute, datetime.datetime):
        new_dict.update({attr: attribute.strftime('%d-%m-%Y %H:%M:%S')})
      if isinstance(attribute, (int, str, float)):
        new_dict.update({attr: attribute})
    return new_dict

  def check_cached_mediadata(self) -> List[Media]:
    if self.force_update:
      if self.use_chunk is False:
        self.logger.info("Collecting user Medias, this might take a while...")
        media_data_obj: List[Media] = self.client.user_medias_gql(user_id=self.user_id)
        serialized_data: dict = self.serialize(obj=media_data_obj)
        if self.data_format == "csv":
          self.logger.info("writing to the csv file...")
          self.update_csv(data=serialized_data)
        if self.data_format == ".json":
          fp = open(self.cache_file, 'w')
          json.dump(serialized_data, fp)
        self.logger.info("Dumped MediaData of user {} in file {}".format((self.user_name or self.user_id),
                                                                         self.cache_file))
        return media_data_obj
      else:
        pass
        # TODO:
    else:
      media_list = []
      fp = open(self.cache_file, 'r')
      serialized_data = json.load(fp)
      for item in serialized_data:
        media_list.append(AttributeDict(serialized_data.get(item, {})))
      return media_list

  def collect(self):
    media_data = self.check_cached_mediadata()
    return media_data


if __name__ == '__main__':
  MediaData(user_name='anninathermopolisrenaldi', force_update=True).collect()
