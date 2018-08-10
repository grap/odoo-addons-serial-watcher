# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OversightProbe(models.Model):
    _name = 'oversight.probe.check'

    # Field Section
    _SELECTION_STATE = [
        ('ok', 'OK'),
        ('error', 'Error'),
    ]

    date_start = fields.Datetime(required=True)

    state = fields.Selection(
        selection=_SELECTION_STATE, string='State', required=True)

    probe_id = fields.Many2one(
        comodel_name='oversight.probe', required=True)
