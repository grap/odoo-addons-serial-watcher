# coding: utf-8
# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib
from openerp import api, fields, models


class OversightProbeVariantHttpCode(models.Model):
    _name = 'oversight.probe.variant.http.code'
    _inherit = ['oversight.probe.variant.mixin']

    _undefined_value = 0
    _variant_value_type = 'integer'
    _variant_probe_type = 'http.code'

    url = fields.Char(string='Url', required=True)

    info_code_list = fields.Char('Info Codes', default='200')

    warning_code_list = fields.Char('Warning Codes')

    # Overload Section
    @api.multi
    def _get_value_string(self, check):
        self.ensure_one()
        if check.value_integer == self._undefined_value:
            return False
        else:
            return str(check.value_integer)

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        value_integer = self._undefined_value
        try:
            response = urllib.urlopen(self.url)
            value_integer = response.code
            if value_integer in self._get_info_codes():
                state = 'info'
            elif value_integer in self._get_warning_codes():
                state = 'warning'
            else:
                state = 'error'
        except Exception as e:
            state = 'critical'
            message = e.message
        return {
            'state': state,
            'message': message,
            'value_integer': value_integer,
        }

    # Custom Section
    @api.multi
    def _get_info_codes(self):
        self.ensure_one()
        res_list = self.info_code_list and self.info_code_list.split(',') or []
        return [int(x) for x in res_list if x.isdigit()]

    @api.multi
    def _get_warning_codes(self):
        self.ensure_one()
        res_list = self.info_code_list and self.info_code_list.split(',') or []
        return [int(x) for x in res_list if x.isdigit()]
