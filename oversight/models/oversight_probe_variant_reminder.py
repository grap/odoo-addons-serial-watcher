# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import _, api, fields, models


class OversightProbeVariantReminder(models.Model):
    _name = 'oversight.probe.variant.reminder'
    _inherit = ['oversight.probe.variant.mixin']

    _variant_value_type = False
    _variant_probe_type = 'reminder'

    warning_date = fields.Datetime(string='Warning Date')

    error_date = fields.Datetime(string='Error Date')

    # Overload Section
    @api.multi
    def _get_value_string(self, check):
        self.ensure_one()
        return False

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        today = datetime.today().strftime('%Y-%m-%d %H:%M')
        if self.error_date and self.error_date > today:
            state = 'error'
            message = _("Expired date: %s" % self.error_date)
        if self.warning_date and self.warning_date > today:
            state = 'warning'
            message = _("Expired date: %s" % self.warning_date)
        else:
            state = 'info'
        return {
            'state': state,
            'message': message
        }
