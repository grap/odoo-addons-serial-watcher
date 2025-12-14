# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import socket

from odoo import _, api, fields, models


class OversightAlert(models.Model):
    _name = "oversight.probe.alert"
    _description = "Oversight Probe Alert"
    _SELECTION_TYPE = [
        ("mail", "EMail"),
    ]

    _SELECTION_SEND_MODE = [
        ("changes", "Changes"),
        ("all", "All"),
    ]

    type = fields.Selection(selection=_SELECTION_TYPE, required=True)

    send_mode = fields.Selection(
        selection=_SELECTION_SEND_MODE, required=True, default="changes"
    )

    probe_template_id = fields.Many2one(
        comodel_name="oversight.probe.template", required=True, ondelete="cascade"
    )

    partner_id = fields.Many2one(comodel_name="res.partner", required=True)

    active_info = fields.Boolean(default=False)

    active_warning = fields.Boolean(default=True)

    active_error = fields.Boolean(default=True)

    active_critical = fields.Boolean(default=True)

    max_try_qty = fields.Integer(
        string="Tries Quantity",
        help="When the quantity is reached, the alert is sent",
        default=1,
    )

    current_failed_qty = fields.Integer(string="Fail Qty", readonly=True)

    # Custom Section
    def _handle_check(self, check):
        for alert in self:
            sent = False
            if check.state == "info":
                if alert.current_failed_qty:
                    if alert.current_failed_qty >= alert.max_try_qty:
                        # An alert has been send, sending a "All is good" alert
                        alert._send_alert(check)
                        sent = True
                    # Reset current_failed_qty
                    alert.current_failed_qty = 0
            else:
                alert_raised = getattr(alert, f"active_{check.state}")
                if alert_raised:
                    alert.current_failed_qty += 1
                    if alert.current_failed_qty == alert.max_try_qty:
                        # Send alert signaling a problem
                        alert._send_alert(check)
                        sent = True
            if alert.send_mode == "all" and not sent:
                # Send email if allways mode is enable
                alert._send_alert(check)

    def _send_alert(self, check):
        for alert in self:
            if alert.type == "mail":
                alert._send_mail(check)

    def _send_mail(self, check):
        mail_obj = self.env["mail.mail"]
        for alert in self:
            partner = alert.partner_id
            if partner.email:
                subject, body = alert._prepare_mail_subject(check)
                mail_vals = {
                    "email_to": partner.email,
                    "subject": subject,
                    "body_html": f"<pre>{body}</pre>",
                }
                mail = mail_obj.sudo().create(mail_vals)
                mail.send(auto_commit=True)

    @api.model
    def _prepare_emoji(self, check):
        if check.state == "info":
            return "👍"
        elif check.state == "warning":
            return "⚠️"
        elif check.state == "error":
            return "👎"
        elif check.state == "critical":
            return "🔥"
        else:
            return "❓"

    def _prepare_mail_subject(self, check):
        self.ensure_one()
        hostname = socket.gethostname()
        probe = check.probe_template_id
        subject = _(
            "%(emoji)s [%(state)s] %(probe_name)s (%(hostname)s)",
            emoji=self._prepare_emoji(check),
            state=check.state,
            probe_name=probe.name,
            hostname=hostname,
        )
        body = _(
            "- Probe Name: %(probe_name)s\n"
            "- State: %(state)s\n"
            "- Date: %(date_start)s\n"
            "- Fail Quantity: %(current_failed_qty)d\n"
            "- Hostname: %(hostname)s\n\n",
            probe_name=probe.name,
            state=check.state,
            date_start=check.date_start,
            current_failed_qty=self.current_failed_qty,
            hostname=hostname,
        )

        if check.value_float != -1:
            body += _("- Value (Float): %(value)s\n", value=check.value_float)
        if check.value_text:
            body += _("- Value (Text): %(value)s\n", value=check.value_text)
        if check.message:
            body += _("- Message: %(message)s\n\n", message=check.message)
        return subject, body
