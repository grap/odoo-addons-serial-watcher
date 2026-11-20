# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint

from odoo import api, fields, models


class OversightServerSoftware(models.Model):
    _name = "oversight.server.software"
    _description = "Server software"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    version = fields.Char()
    color = fields.Integer(default=lambda x: x._default_color(), aggregator=False)

    def _default_color(self):
        return randint(1, 11)

    @api.depends("name", "version")
    def _compute_display_name(self):
        for software in self:
            software.display_name = str(software.name) + " " + str(software.version)
