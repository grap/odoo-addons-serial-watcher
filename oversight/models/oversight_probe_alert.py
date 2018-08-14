# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    # Custom Section
    def _get_translation(self, lang, text):
        context = {'lang': lang}  # noqa: _() checks page for locals
        return _(text)

    @api.multi
    def send_alert(self, check):
        for alert in self:
            if alert.type == 'mail':
                alert.send_mail(check)

    @api.multi
    def send_mail(self, check):
        mail_obj = self.env['mail.mail']
        for alert in self:
            partner = alert.partner_id
            if partner.email:
                probe = check.probe_template_id
                subject = self._get_translation(
                    partner.lang, _('[%s] %s') % (check.state, probe.name))
                body = self._get_translation(
                    partner.lang, _(
                        "- Probe Name: %s\n\n"
                        "- State: %s\n\n"
                        "- Float Value: %s\n\n"
                        "- Text Value: %s\n\n"
                        "- Date: %s\n\n"
                        "- Message: %s\n\n"
                    ) % (
                        probe.name,
                        check.state,
                        check.value_float,
                        check.value_text,
                        check.date_start,
                        check.message))
                mail_vals = {
                    'email_to': partner.email,
                    'subject': subject,
                    'body_html': '<pre>%s</pre>' % body,
                }
                mail = mail_obj.sudo().create(mail_vals)
                mail.send(auto_commit=True)
