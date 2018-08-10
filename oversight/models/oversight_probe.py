# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from datetime import datetime

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OversightProbe(models.Model):
    _name = 'oversight.probe'

    # Field Section
    _SELECTION_PROBE_TYPE = [
        ('ping', 'Ping'),
        ('http', 'HTTP'),
    ]

    name = fields.Char(required=True)

    probe_type = fields.Selection(
        selection=_SELECTION_PROBE_TYPE, string='Type', required=True)

    target = fields.Char(required=True)

    # View Section
    @api.multi
    def button_execute(self):
        return self._oversight()

    # Private Section
    @api.multi
    def _oversight(self):
        check_obj = self.env['oversight.probe.check']
        for probe in self:
            # Recover generic information
            date_start = datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)

            # Type1. Ping Execution
            if probe.probe_type == 'ping':
                response = os.system("ping -c 1 %s" % probe.target)
                if response == 0:
                    state = 'ok'
                else:
                    state = 'error'

            value = {
                'date_start': date_start,
                'state': state,
                'probe_id': probe.id,
            }
            check_obj.create(value)
