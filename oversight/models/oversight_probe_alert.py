# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import socket

from openerp import _, api, fields, models


class OversightAlert(models.Model):
    _name = 'oversight.probe.alert'

    _SELECTION_TYPE = [
        ('mail', 'EMail'),
    ]

    _SELECTION_SEND_MODE = [
        ('changes', 'Changes'),
        ('all', 'All'),
    ]

    # Field Section
    type = fields.Selection(
        selection=_SELECTION_TYPE, string='Type', required=True)

    send_mode = fields.Selection(
        selection=_SELECTION_SEND_MODE, string='Send Mode', required=True,
        default='changes')

    probe_template_id = fields.Many2one(
        comodel_name='oversight.probe.template', required=True)

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True)

    active_info = fields.Boolean(default=False)

    active_warning = fields.Boolean(default=True)

    active_error = fields.Boolean(default=True)

    active_critical = fields.Boolean(default=True)

    max_try_qty = fields.Integer(
        string='Tries Quantity',
        help="When the quantity is reached, the alert is sent", default=1)

    current_failed_qty = fields.Integer(
        string='Fail Qty', readonly=True)

    # Custom Section
    def _get_translation(self, lang, text):
        context = {'lang': lang}  # noqa: _() checks page for locals
        return _(text)

    @api.multi
    def _handle_check(self, check):
        for alert in self:
            sent = False
            if check.state == 'info':
                if alert.current_failed_qty:
                    if alert.current_failed_qty >= alert.max_try_qty:
                        # An alert has been send, sending a "All is good" alert
                        alert._send_alert(check)
                        sent = True
                    # Reset current_failed_qty
                    alert.current_failed_qty = 0
            else:
                alert_raised = getattr(alert, 'active_%s' % check.state)
                if alert_raised:
                    alert.current_failed_qty += 1
                    if alert.current_failed_qty == alert.max_try_qty:
                        # Send alert signaling a problem
                        alert._send_alert(check)
                        sent = True
            if alert.send_mode == 'all' and not sent:
                # Send email if allways mode is enable
                alert._send_alert(check)

    @api.multi
    def _send_alert(self, check):
        for alert in self:
            if alert.type == 'mail':
                alert._send_mail(check)

    @api.multi
    def _send_mail(self, check):
        mail_obj = self.env['mail.mail']
        for alert in self:
            partner = alert.partner_id
            if partner.email:
                subject, body = self._prepare_mail_subject(alert, check)
                mail_vals = {
                    'email_to': partner.email,
                    'subject': subject,
                    'body_html': '<pre>%s</pre>' % body,
                }
                mail = mail_obj.sudo().create(mail_vals)
                mail.send(auto_commit=True)

    @api.model
    def _prepare_mail_subject(self, alert, check):
        hostname = socket.gethostname()
        probe = check.probe_template_id
        partner = alert.partner_id
        if check.state == 'info':
            emoji = u'👍'
        else:
            emoji = u'🔥'
        subject = self._get_translation(partner.lang, _(
            '%s [%s] %s (%s)') % (
            emoji, check.state, probe.name, hostname))
        body = self._get_translation(
            partner.lang, _(
                "- Probe Name: %s\n"
                "- State: %s\n"
                "- Date: %s\n"
                "- Fail Quantity: %d\n"
                "- Hostname: %s\n\n"
            ) % (
                probe.name,
                check.state,
                check.date_start,
                alert.current_failed_qty,
                hostname))

        if check.value_float != -1:
            body += self._get_translation(
                partner.lang, _("- Value (Float): %s\n") % (
                    check.value_float))
        if check.value_text:
            body += self._get_translation(
                partner.lang, _("- Value (Text): %s\n") % (
                    check.value_text))
        if check.message:
            body += self._get_translation(
                partner.lang, _("- Message: %s\n\n") % (
                    check.message))
        return subject, body
