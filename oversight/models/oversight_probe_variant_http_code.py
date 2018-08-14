# coding: utf-8
# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib
from openerp import api, fields, models


class OversightProbeVariantHttpCode(models.Model):
    _name = 'oversight.probe.variant.http.code'
    _inherits = {'oversight.probe.template': 'probe_template_id'}
    _order = 'name'

    _variant_probe_type = 'http.code'

    url = fields.Char(string='Url', required=True)

    probe_template_id = fields.Many2one(
        comodel_name='oversight.probe.template', string='Probe Template',
        required=True, ondelete="cascade", select=True, auto_join=True)

    @api.model
    def default_get(self, fields):
        res = super(OversightProbeVariantHttpCode, self).default_get(fields)
        res.update({'probe_type': self._variant_probe_type})
        return res

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        try:
            response = urllib.urlopen(self.url)
            if response.code == 200:
                state = 'info'
            else:
                state = 'error'
                message = "Http Code is %s" % response
        except Exception as e:
            state = 'critical'
            message = e.message
        return {
            'state': state,
            'message': message,
        }
