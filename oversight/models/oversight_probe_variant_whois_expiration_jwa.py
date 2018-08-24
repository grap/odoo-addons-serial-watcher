# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime


from openerp import _, api, fields, models


class OversightProbeVariantWhoisExpirationJwa(models.Model):
    _name = 'oversight.probe.variant.whois.expiration.jwa'
    _inherit = [
        'oversight.probe.json.mixin',
        'oversight.probe.variant.mixin',
    ]

    _undefined_value = -9999
    _variant_value_type = 'float'
    _variant_probe_type = 'whois.expiration.jwa'

    _base_json_url = "https://jsonwhoisapi.com/api/v1/whois?identifier="
    _json_required_keys = ['expires', 'registered']
    _json_auth_method = 'ir.config_parameter'

    url = fields.Char(required=True)

    warning_days_threshold = fields.Integer(required=True, default=30)

    error_days_threshold = fields.Integer(required=True, default=7)

    # Overload Section
    @api.multi
    def _prepare_full_url(self):
        self.ensure_one()
        return self._base_json_url + self.url

    @api.multi
    def _get_value_string(self, check):
        self.ensure_one()
        if check.value_integer == self._undefined_value:
            return False
        else:
            return _('D - %d') % (check.value_integer)

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        value_integer = self._undefined_value
        try:
            res = self._json_execute()
            if not res['registered']:
                raise Exception(_("%s is not registered") % self.url)
            expire_date = datetime.strptime(
                res['expires'], "%Y-%m-%d %H:%M:%S")
            value_integer = (expire_date - datetime.now()).days
            if value_integer <= self.error_days_threshold:
                state = 'error'
            elif value_integer <= self.warning_days_threshold:
                state = 'warning'
            else:
                state = 'info'
            message = "Expire Date %s" % (res['expires'])
        except Exception as e:
            state = 'critical'
            message = e.message
        return {
            'state': state,
            'message': message,
            'value_integer': value_integer,
        }
