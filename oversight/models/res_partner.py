# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = ["res.partner"]

    url_ids = fields.One2many(comodel_name="oversight.url", inverse_name="partner_id")
