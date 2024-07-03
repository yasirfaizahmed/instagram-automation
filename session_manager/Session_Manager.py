# ############ References
# https://adw0rd.github.io/instagrapi/usage-guide/best-practices.html


import time
from threading import Thread
import queue
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import os

from patterns.Patterns import Singleton
from base.base import Base
from session_manager.Session_Config import SessionConfig


START_TIME = time.time()
SESSION_TIME = 5 * 60    # seconds


class SessionManager(Base, SessionConfig, metaclass=Singleton):
  def __init__(self, session_time: int = SESSION_TIME):
    # super().__init__(self)
    self._session_time = session_time
    self._session_thread: Thread = None
    self._session_queue = queue.Queue(maxsize=10)
    self._active_session: Client = Client()

    if os.path.exists(self.settings_path) is False:
      os.mkdir("configs")
      open("configs/settings.json", "w").close()
      self.logger.info("No cached settings were found, creating a new one")
      self._active_session.login(**self.account_creds)
      self._active_session.dump_settings(self.settings_path)    # caching settings
    else:
      _ses = self._active_session.load_settings(self.settings_path)    # loading settings
      self._active_session.set_settings(_ses)
      self._active_session.login(**self.account_creds)
      # check if session is valid
      try:
        self._active_session.get_timeline_feed()
      except LoginRequired:
        self.logger.info("Session is invalid, need to login via username and password")
        old_session = self._active_session.get_settings()
        # use the same device uuids across logins
        self._active_session.set_settings({})
        self._active_session.set_uuids(old_session["uuids"])
        self._active_session.login(**self.account_creds)

    try:
      self._account_inf = self._active_session.account_info()
    except LoginRequired:
      self._active_session.relogin()    # clean session
      self._active_session.dump_settings(self.settings_path)    # caching settings

    self.initialize_session_manager()
    self.logger.info("Creating the first client session")

  @property
  def active_session(self):
    return self._active_session

  @property
  def session_time(self):
    pass

  @session_time.setter
  def session_time(self, new_session_time):
    self._session_time = new_session_time

  def _session_thread_target(self):
    start_time = time.time()
    while True:
      current_time = time.time()
      if (current_time - start_time) > self._session_time:
        self._active_session = Client()
        _ses: dict = self._active_session.load_settings(self.settings_path)    # loading settings
        self._active_session.set_settings(_ses)
        self._active_session.login(**self.account_creds)

        # check if session is valid
        try:
          self._active_session.get_timeline_feed()
        except LoginRequired:
          self.logger.info("Session is invalid, need to login via username and password")
          old_session = self._active_session.get_settings()
          # use the same device uuids across logins
          self._active_session.set_settings({})
          self._active_session.set_uuids(old_session["uuids"])
          self._active_session.login(**self.account_creds)

        session_item = {'stamp': current_time - START_TIME,
                        'active_session_id': self._active_session,
                        'all_tasks_done': self._session_queue.all_tasks_done}
        start_time = current_time
        if self._session_queue.qsize() == 10:
          self._session_queue.get()   # pop the early session item
          self.logger.info("Popping session of time_stamp: {}".format(session_item.get('stamp')))
        self._session_queue.put(session_item)   # add the recently created session item
        self.logger.warning("Session Timeout, creating new session...")
      time.sleep(1)

  def initialize_session_manager(self):
    self._session_thread = Thread(target=self._session_thread_target, args=[])
    self._session_thread.start()


if __name__ == '__main__':
  sm = SessionManager()
