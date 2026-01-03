# Copyright 2022 Sharuzzaman Ahmat Raslan <sharuzzaman@gmail.com>
# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import socket

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class OversightUrl(models.Model):
    _name = "oversight.url"
    _inherit = ["probe.mixin.certificate", "probe.mixin.http.response"]
    _description = "URL"
    _order = "name"

    name = fields.Char(required=True)

    active = fields.Boolean(default=True, tracking=True)

    domain_name_id = fields.Many2one(
        comodel_name="oversight.domain.name",
        ondelete="restrict",
        readonly=True,
    )

    server_id = fields.Many2one(
        comodel_name="oversight.server",
        ondelete="restrict",
        readonly=True,
    )

    service_id = fields.Many2one(
        comodel_name="oversight.service",
        ondelete="restrict",
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "This URL already exists.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" in vals:
                vals["name"] = self._clean_url(vals["name"])
        urls = super().create(vals_list)
        urls._compute_domain_name_id()
        urls._compute_server_id()
        return urls

    def write(self, vals):
        if "name" in vals:
            vals["name"] = self._clean_url(vals["name"])
        res = super().write(vals)
        if "name" in vals:
            self._compute_domain_name_id()
            self._compute_server_id()
        return res

    @api.model
    def _clean_url(self, url):
        if not url:
            return False
        while url.endswith("/"):
            url = url[:-1]
        url = url.replace("http://", "").replace("https://", "")
        return url

    def _compute_domain_name_id(self):
        OversightDomainName = self.env["oversight.domain.name"]
        for url in self:
            if not self._clean_url(url.name) or "." not in self._clean_url(url.name):
                url.domain_name_id = False
                continue
            domain = ".".join(self._clean_url(url.name).split(".")[-2:])

            domain_name = OversightDomainName.with_context(active_test=False).search(
                [("name", "=", domain)], limit=1
            )
            if not domain_name:
                domain_name = OversightDomainName.create({"name": domain})
            url.domain_name_id = domain_name

    def _compute_server_id(self):
        OversightServer = self.env["oversight.server"]
        for url in self:
            if not self._clean_url(url.name) or "." not in self._clean_url(url.name):
                url.server_id = False
                continue
            try:
                ip = socket.gethostbyname(self._clean_url(url.name))
                server = OversightServer.with_context(active_test=False).search(
                    [("ip", "=", ip)], limit=1
                )
                if not server:
                    server = OversightServer.create({"ip": ip, "ping_active": False})
                url.server_id = server
            except socket.gaierror:
                message = _(
                    "Unable to deduce server IP from the URL '%(url)s'",
                    url=self._clean_url(url.name),
                )
                _logger.error(message)
                self.env.user.notify_danger(message)
                url.server_id = False
                continue

    @api.model
    def cron_update_certificate_information(self):
        self.search([])._probe_certificate_get_information()

    def button_update_certificate_information(self):
        self._probe_certificate_get_information()
