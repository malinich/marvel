# coding: utf-8
import hashlib

import time

from requests import RequestException

from .conf import *

import requests
import logging

logger = logging.getLogger()


class SimpleRouter(object):
    BASE_URL = "https://gateway.marvel.com:443/v1/public"
    COMICS_URL = BASE_URL + "/comics"
    COMICS_ID_URL = COMICS_URL + "/{obj_id}"

    def resolve(self, url, params=None):
        if not params:
            params = {}

        return url.format(**params)


class MarvelService(object):
    """

    """

    def __init__(self):
        self.router = SimpleRouter()

    def get_comic(self, obj_id):
        url = self.router.resolve(SimpleRouter.COMICS_ID_URL, {"obj_id": obj_id})
        r = self._do(url)
        return r

    def get_comics(self, limit):
        url = self.router.resolve(SimpleRouter.COMICS_URL)

        params = {
            "limit": limit,
        }
        r = self._do(url, params)
        return r

    def get_comics_by_title(self, title):
        """
         https://gateway.marvel.com:443/v1/public/comics?titleStartsWith=start&limit=2&apikey=xxxxx

        :param title:
        :type title:
        :return:
        :rtype:
        """
        url = self.router.resolve(SimpleRouter.COMICS_URL)

        params = {
            "titleStartsWith": title,
        }

        r = self._do(url, params)
        return r

    # private
    def _do(self, url, additional_params=None):
        if additional_params is None:
            additional_params = {}

        ts = int(time.time())

        params = {
            "ts": ts,
            "apikey": PUBLIC_KEY,
            "hash": self._generate_hash(ts)
        }
        params.update(additional_params)

        r = requests.get(url, params=params)
        if r.status_code == requests.codes.ok:
            data = r.json()
        elif requests.codes.bad <= r.status_code >= requests.codes.server_error:
            logger.exception(r.content)
            raise RequestException(r.content)
        else:
            data = {}
        return data

    def _generate_hash(self, ts):
        """

        :param ts:
        :type ts:
        :return:
        :rtype: basestring
        """
        m = hashlib.md5("{}{}{}".format(
            ts,
            PRIVATE_KEY,
            PUBLIC_KEY
        ))
        return m.hexdigest()
