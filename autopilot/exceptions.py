"""

Defines custom exceptions

"""


class AutopilotException(Exception):
    pass


class ScreenException(AutopilotException):
    pass


class TrainException(AutopilotException):
    pass