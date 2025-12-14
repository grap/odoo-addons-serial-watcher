# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OversightDomainName(models.Model):
    _name = "oversight.domain.name"
    _description = "Domain Name"
    _rec_name = "domain_name"

    domain_name = fields.Char(required=True)
