# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    registrar_warning_threshold = fields.Integer(
        string="Registrar Warning (in Days)",
        config_parameter="oversight.registrar_warning_threshold",
    )

    certificate_warning_threshold = fields.Integer(
        string="Certificate Warning (in Days)",
        config_parameter="oversight.certificate_warning_threshold",
    )
