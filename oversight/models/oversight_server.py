# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models

from .probe_result import _PROBE_CHECK_STATE_SELECTION


class OversightServer(models.Model):
    _name = "oversight.server"
    _inherit = ["probe.mixin.ping"]
    _description = "server"

    name = fields.Char(compute="_compute_name", store=True)

    active = fields.Boolean(default=True, tracking=True)

    technical_name = fields.Char()

    services = fields.Char()

    service_ids = fields.Many2many(
        comodel_name="oversight.service", compute="_compute_service_ids"
    )

    ip = fields.Char(required=True)

    ssh_authentication = fields.Many2one(comodel_name="oversight.ssh.authentication")

    is_ours = fields.Boolean()

    url_ids = fields.One2many(
        comodel_name="oversight.url", inverse_name="server_id", readonly=True
    )

    url_qty = fields.Integer(compute="_compute_url_qty", store=True)

    monthly_cost = fields.Monetary(currency_field="currency_id")

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="company_id.currency_id"
    )

    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda x: x.env.company.id
    )

    invoice_partner_id = fields.Many2one(
        comodel_name="res.partner", domain=[("is_company", "=", True)]
    )

    supplier_partner_id = fields.Many2one(
        comodel_name="res.partner", domain=[("is_company", "=", True)]
    )

    data_center = fields.Char()

    server_identifier = fields.Char()

    server_model_name = fields.Char()

    _sql_constraints = [
        (
            "ip_uniq",
            "unique (ip)",
            "A server with the same IP already exists.",
        ),
    ]

    ping_active = fields.Boolean(default=True, tracking=True)

    ping_qty = fields.Integer("Result Count", compute="_compute_ping_qty")

    ping_state = fields.Selection(
        selection=_PROBE_CHECK_STATE_SELECTION,
        readonly=True,
        default="01_unknown",
        tracking=True,
    )

    ping_error_message = fields.Char(readonly=True, tracking=True)

    @api.depends("ip", "technical_name")
    def _compute_name(self):
        for server in self:
            if server.technical_name:
                server.name = f"{server.technical_name} ({server.ip})"
            elif server.ip:
                server.name = f"{server.ip}"
            else:
                server.name = "/"

    @api.depends("url_ids.service_id")
    def _compute_service_ids(self):
        for server in self:
            server.service_ids = server.mapped("url_ids.service_id")

    @api.depends("url_ids.server_id")
    def _compute_url_qty(self):
        for server in self:
            server.url_qty = len(server.url_ids)

    def _compute_ping_qty(self):
        probe_result_count_dict = self._compute_result_qty("ping")
        for record in self:
            record.ping_qty = probe_result_count_dict.get(record.id, 0)

    @api.model
    def cron_probe_ping_check(self):
        self.search([("ping_active", "=", True)]).button_probe_ping_check()

    def button_probe_ping_check(self):
        self._probe_ping_check()

    def action_view_probe_result_ping(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "oversight.action_probe_result"
        )
        action["domain"] = [
            ("res_name", "=", "oversight.server"),
            ("res_id", "in", self.ids),
        ]
        return action
