"""OKTA API Client"""

import requests

from theocktany.conf import settings
from theocktany.exceptions import (
    ApiException,
    SerializerException,
)

__all__ = ['ApiClient', ]


class ApiClient(object):

    def __init__(self, **kwargs):
        self.settings = settings

        # any values passed in kwargs will be a setting
        for key, value in kwargs.items():
            self.settings.set(key, value)

    @property
    def _headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'SSWS ' + self.settings.get('API_TOKEN'),
        }

    @property
    def _base_url(self):
        return self.settings.get('BASE_URL')

    def get(self, path, params=None):
        response = requests.get(self._base_url+path, params=params, headers=self._headers)

        if response is None:
            raise ApiException('No response received.')
        return response.content.decode('UTF-8'), response.status_code

    def post(self, path, data=None):
        response = requests.post(self._base_url+path, json=data, headers=self._headers)

        if response is None:
            raise ApiException('No response received.')
        try:
            response_dict = response.json()
            return response_dict, response.status_code
        except ValueError:
            raise ApiException('Response was invalid.')
