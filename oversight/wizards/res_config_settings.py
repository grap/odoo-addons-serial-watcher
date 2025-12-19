# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


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

    summary_recipient_user_id = fields.Many2one(
        comodel_name="res.users",
        config_parameter="oversight.summary_recipient_user_id",
    )

    @api.model
    def cron_oversight_send_summary_email(self):
        icp = self.env["ir.config_parameter"].sudo()
        user_id = int(icp.get_param("oversight.summary_recipient_user_id"))
        if user_id:
            self._oversight_send_summary_email(self.env["res.users"].browse(user_id))

    def button_oversight_send_summary_email(self):
        if self.summary_recipient_user_id:
            self._oversight_send_summary_email(self.summary_recipient_user_id)

    def _oversight_send_summary_email(self, user):
        template = self.env.ref("oversight.email_template_summary")
        template.send_mail(
            res_id=user.id,
            force_send=True,
        )
