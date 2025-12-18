# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = ["res.users"]

    def oversight_get_data(self, data_type):
        if data_type == "domain_name_probe_fails":
            return self.env["oversight.domain.name"].search(
                [("registrar_probe_last_state", "=", "02_probe_failed")]
            )
        elif data_type == "url_probe_fails":
            return self.env["oversight.url"].search(
                [("certificate_probe_last_state", "=", "02_probe_failed")]
            )
        if data_type == "domain_name_probe_errors":
            return (
                self.env["oversight.domain.name"]
                .search([("registrar_probe_last_state", "!=", "02_probe_failed")])
                .filtered(lambda x: x.registrar_probe_state == "error")
            )
        if data_type == "url_probe_errors":
            return (
                self.env["oversight.url"]
                .search([("certificate_probe_last_state", "!=", "02_probe_failed")])
                .filtered(lambda x: x.certificate_probe_state == "error")
            )
        if data_type == "domain_name_probe_warnings":
            return (
                self.env["oversight.domain.name"]
                .search([("registrar_probe_last_state", "!=", "02_probe_failed")])
                .filtered(lambda x: x.registrar_probe_state == "warning")
            )
        if data_type == "url_probe_warnings":
            return (
                self.env["oversight.url"]
                .search([("certificate_probe_last_state", "!=", "02_probe_failed")])
                .filtered(lambda x: x.certificate_probe_state == "warning")
            )

        return []
