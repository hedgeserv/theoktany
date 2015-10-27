import os

from . import global_settings


# TODO: shair: This will probably need to be expanded in the future
class LazySettings(object):
    """Get a setting either from an environment variable or the global settings"""

    def __init__(self, **kwargs):
        self._instance_settings = {}

        # this will put values into _instance_settings
        for key, value in kwargs.items():
            self._instance_settings['key'] = value

    def set(self, item, value):
        self._instance_settings[item] = value

    def get(self, item, default=None):

        if item in self._instance_settings:
            return self._instance_settings[item]

        return os.getenv('THEOKTANY_'+item, None) or getattr(global_settings, item, None) or default


settings = LazySettings()
