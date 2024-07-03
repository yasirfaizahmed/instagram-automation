import os
import json


class SessionConfig():
  file_path = os.environ.get("meta_accounts_data", None)
  settings_path = 'configs/settings.json'

  # Data as a whole
  data: dict = json.load(open(file_path, 'r'))

  # automated account creds
  account_creds = data.get("automated_acccount", {}).get('creds', {})

  # suspected account handles
  suspected_accounts = data.get("suspected_accounts", {})
