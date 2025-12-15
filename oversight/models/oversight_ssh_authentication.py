# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class OversightSshAuthentication(models.Model):
    _name = "oversight.ssh.authentication"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "SSH Authentication"
    _rec_name = "login"

    login = fields.Char(required=True)
