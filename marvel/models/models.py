# -*- coding: utf-8 -*-

from odoo import models, fields


class Comics(models.Model):
    _name = 'marvel.comics'

    title = fields.Char()
    description = fields.Text()

    price = fields.Integer()
    dates = fields.Datetime("Issue date")

    images = fields.One2many("marvel.image", "comic", string="images")
    characters = fields.One2many("marvel.character", "comic", string="characters")
    stories = fields.One2many("marvel.story", "comic", string="stories")

    is_visible = fields.Boolean(default=False)


class Image(models.Model):
    _name = "marvel.image"
    path = fields.Char()
    comic = fields.Many2one("marvel.comics")


class Character(models.Model):
    _name = "marvel.character"

    name = fields.Char()
    comic = fields.Many2one("marvel.comics")


class Story(models.Model):
    _name = "marvel.story"

    name = fields.Char()
    comic = fields.Many2one("marvel.comics")
