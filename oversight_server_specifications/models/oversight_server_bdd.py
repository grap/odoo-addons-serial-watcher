# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint

from odoo import api, fields, models


class OversightServerBdd(models.Model):
    _name = "oversight.server.bdd"
    _description = "Server Bdd"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    version = fields.Float()
    color = fields.Integer(default=lambda x: x._default_color(), aggregator=False)

    def _default_color(self):
        return randint(1, 11)

    @api.depends("name", "version")
    def _compute_display_name(self):
        for bdd in self:
            bdd.display_name = str(bdd.name) + " " + str(bdd.version)
