# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from openerp import api, fields, models


class OversightProbeVariantPing(models.Model):
    _name = 'oversight.probe.variant.ping'
    _inherit = ['oversight.probe.variant.mixin']

    _variant_probe_type = 'ping'

    destination = fields.Char(
        string='Destination Computer', required=True)

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        try:
            response = os.system("ping %s -c 1" % (self.destination))
            if response == 0:
                state = 'info'
            else:
                state = 'error'
        except Exception as e:
            state = 'critical'
            message = e.message
        return {
            'state': state,
            'message': message
        }
