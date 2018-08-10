# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from datetime import datetime

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OversightProbe(models.Model):
    _name = 'oversight.probe'
    _order = 'name'

    # Field Section
    _SELECTION_PROBE_TYPE = [
        ('ping', 'Ping'),
        ('http', 'HTTP'),
    ]

    _SELECTION_STATE = [
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ]

    _SELECTION_INTERVAL_TYPE = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('work_days', 'Work Days'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]

    state = fields.Selection(
        selection=_SELECTION_STATE, string='state', readonly=True,
        default='draft')

    name = fields.Char(required=True)

    probe_type = fields.Selection(
        selection=_SELECTION_PROBE_TYPE, string='Type', required=True)

    target = fields.Char(required=True)

    cron_id = fields.Many2one(
        comodel_name='ir.cron')

    interval_number = fields.Integer(
        string='Interval Number', default=1, required=True,
        help="Repeat every x.", )

    interval_type = fields.Selection(
        string='Interval Unit', selection=_SELECTION_INTERVAL_TYPE,
        default='minutes', required=True)

    # View Section
    @api.multi
    def button_execute(self):
        return self._run_oversight()

    @api.multi
    def button_confirm(self):
        cron_obj = self.env['ir.cron']
        for probe in self.filtered(lambda x: x.state == 'draft'):
            probe.cron_id = cron_obj.create(probe._prepare_cron())
            probe.state = 'confirm'

    @api.multi
    def button_draft(self):
        for probe in self.filtered(lambda x: x.state == 'confirm'):
            probe.cron_id.unlink()
            probe.state = 'draft'

    @api.model
    def cron_execute(self, ids):
        items = self.browse(ids)
        items._run_oversight()

    # Private Section
    @api.multi
    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _('Probe %s') % (self.name),
            'user_id': SUPERUSER_ID,
            'model': 'oversight.probe',
            'function': 'cron_execute',
            'numbercall': -1,
            'args': repr(([self.id],)),
            'interval_number': self.interval_number,
            'interval_type': self.interval_type,
        }

    @api.multi
    def _run_oversight(self):
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
