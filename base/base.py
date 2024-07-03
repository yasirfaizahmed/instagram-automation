from log_handling.log_handling import InitilizeLogger


class Base():
  logger = InitilizeLogger(level=10)()
