# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint

from odoo import fields, models


class OversightService(models.Model):
    _name = "oversight.service"
    _description = "Service"

    name = fields.Char(required=True)

    color = fields.Integer(default=lambda x: x._default_color(), aggregator=False)

    url_ids = fields.One2many(comodel_name="oversight.url", inverse_name="service_id")

    server_ids = fields.One2many(
        comodel_name="oversight.url", inverse_name="service_id"
    )

    def _default_color(self):
        return randint(1, 11)
