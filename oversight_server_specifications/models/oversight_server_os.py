# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OversightServerOS(models.Model):
    _name = "oversight.server.os"
    _description = "Server OS"

    name = fields.Char()
