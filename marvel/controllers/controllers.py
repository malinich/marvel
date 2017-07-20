# -*- coding: utf-8 -*-

import logging
import pprint
from itertools import islice

from addons.marvel.exceptions import Empty
from addons.marvel.models import Comics
from odoo import http
from .. import service
from ..utils import get_item, parse_data

logger = logging.getLogger(__name__)


class Marvel(http.Controller):
    @http.route('/marvel/', auth='public', website=True)
    def index(self, **kw):
        comics = service.get_comics(30)
        data, _ = get_item(comics, 'data', 'results')

        logger.debug("DATA:{}".format(data))
        return http.request.render('marvel.index', {
            'root': '/marvel/marvel',
            'objects': data
        })

    @http.route('/marvel/objects/', auth='public', website=True)
    def list(self, **kw):
        comics = service.get_comics(30)
        data, _ = get_item(comics, 'data', 'results')

        return http.request.render('marvel.listing', {
            'root': '/marvel/',
            'objects': data
        })

    @http.route('/marvel/objects/<obj_id>/', auth='public', website=True)
    def object(self, obj_id, **kw):
        logger.debug("obj: {}".format(obj_id))

        resp = service.get_comic(obj_id)
        logger.debug("DATA:{}".format(resp))

        try:
            data = self._fetch_result(resp, 'data', 'results', 0)
        except Empty:
            return http.request.render('marvel.empty', {
                'root': '/marvel/',
            })

        comic = self._parse_comic(data)
        logger.debug("comic:{}".format(comic))

        return http.request.render('marvel.object', {
            'object': comic
        })

    @http.route('/marvel/find/', auth='public', website=True)
    def find(self, **kw):
        title = http.request.params.get('title')
        if title:
            resp = service.get_comics_by_title(title)
            logger.debug("DATA:{}".format(resp))

            try:
                data = self._fetch_result(resp, 'data', 'results')
            except Empty:
                return http.request.render('marvel.object_empty', {
                    'root': '/marvel/',
                })

            comics = map(self._parse_comic, data)

            logger.debug("DATA:{}".format(comics))
            return http.request.render('marvel.listing', {
                'root': '/marvel/',
                'objects': comics
            })

    @http.route('/marvel/save/', auth='public', website=True)
    def save(self, **kw):
        obj_id = http.request.params.get('obj_id')
        logger.debug("obj_id: {}".format(obj_id))
        if obj_id:
            resp = service.get_comic(obj_id)
            logger.debug("DATA:{}".format(resp))

            try:
                data = self._fetch_result(resp, 'data', 'results', 0)
            except Empty:
                return http.request.render('marvel.object_empty', {
                    'root': '/marvel/',
                })

            data = self._parse_comic(data)

            comic = self._save_comic(data)
            self._save_images(data['images'], comic)
            self._save_characters(data['characters'], comic)
            self._save_stories(data['stories'], comic)

            logger.debug("save_data:{}".format(comic))

            return http.request.render('marvel.save', {
                'root': '/marvel/',
            })

    def _fetch_result(self, response, *attrs):
        row_data, _ = get_item(response, *attrs)

        if not row_data:
            raise Empty()
        return row_data

    def _parse_comic(self, row_data):
        """

        :param row_data:
        :type row_data:
        :return:
        :rtype: dict
        """
        data = parse_data(row_data, {
            "id": "id",
            "title": "title",
            "description": "description",
            "images": ['path', "extension"],
            "characters": {'items': ["name"]},
            "stories": {'items': ["name"]},
            "prices": "price",
            "dates": {"_filter": lambda d: d['type'] == "focDate",
                      "_take": lambda d: self._parse_date(d["date"])}
        })
        d1 = islice(data.get('images', []), 0, None, 2)
        d2 = islice(data.get('images', []), 1, None, 2)

        data['images'] = map(lambda i: i[0] + "." + i[1], zip(d1, d2))

        return data

    def _save_comic(self, data):
        logger.debug("DATA:{}".format(data))
        params = {
            "title": data['title'],
            "description": data['description'],
            "dates": data['dates'],
        }
        logger.debug("params:{}".format(params))
        comic = http.request.env['marvel.comics'].create(params)
        return comic

    def _save_images(self, images, comic):
        logger.debug("_save_images:{}".format(comic.id))
        save_images = [
            http.request.env['marvel.image'].create(
                {
                    "path": image,
                    "comic": comic.id
                 }
            )
            for image in images
        ]
        return save_images

    def _save_characters(self, characters, comic):
        logger.debug("_save_characters:{}".format(comic.id))
        save_images = [
            http.request.env['marvel.character'].create(
                {
                    "name": character,
                    "comic": comic.id
                 }
            )
            for character in characters
        ]
        return save_images

    def _save_stories(self, stories, comic):
        logger.debug("_save_characters:{}".format(comic.id))
        save_images = [
            http.request.env['marvel.story'].create(
                {
                    "name": story,
                    "comic": comic.id
                 }
            )
            for story in stories
        ]
        return save_images

    @staticmethod
    def _parse_date(date):
        """
        :type date: str
        :rtype: str
        """
        if date.startswith("-"):
            return None
        return date
