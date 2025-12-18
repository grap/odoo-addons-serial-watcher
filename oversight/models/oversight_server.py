# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class OversightServer(models.Model):
    _name = "oversight.server"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "server"

    name = fields.Char(compute="_compute_name", store=True)

    active = fields.Boolean(default=True, tracking=True)

    technical_name = fields.Char()

    services = fields.Char()

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

    @api.depends("ip", "technical_name")
    def _compute_name(self):
        for server in self:
            if server.technical_name:
                server.name = f"{server.technical_name} ({server.ip})"
            elif server.ip:
                server.name = f"{server.ip}"
            else:
                server.name = "/"

    @api.depends("url_ids.server_id")
    def _compute_url_qty(self):
        for server in self:
            server.url_qty = len(server.url_ids)
