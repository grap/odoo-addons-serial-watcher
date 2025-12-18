# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OversightDomainName(models.Model):
    _name = "oversight.domain.name"
    _inherit = ["probe.mixin.registrar"]
    _description = "Domain Name"

    name = fields.Char(required=True)

    url_ids = fields.One2many(
        comodel_name="oversight.url", inverse_name="domain_name_id", readonly=True
    )

    url_qty = fields.Integer(compute="_compute_url_qty", store=True)

    @api.depends("url_ids.server_id")
    def _compute_url_qty(self):
        for server in self:
            server.url_qty = len(server.url_ids)

    @api.model
    def cron_update_registrar_info(self):
        self.search([]).button_update_registrar_info()

    def button_update_registrar_info(self):
        self._probe_registrar_get_information()
