# Copyright (C) 2026 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class OversightServer(models.Model):
    _inherit = "oversight.server"

    ram = fields.Integer()
    hard_drive_capacity = fields.Integer()
    hard_drive_type = fields.Selection(
        [("ssd", "SSD"), ("mechanical", "Mechanical")],
        default="ssd",
    )
    os = fields.Many2one(comodel_name="oversight.server.os")
    cpu = fields.Many2one(comodel_name="oversight.server.cpu")
    cpu_note = fields.Integer(related="cpu.note")
