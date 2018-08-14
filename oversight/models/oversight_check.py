# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OversightCheck(models.Model):
    _name = 'oversight.check'
    _order = 'date_start desc'

    # Field Section
    _SELECTION_STATE = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    date_start = fields.Datetime(required=True)

    state = fields.Selection(
        selection=_SELECTION_STATE, string='State', required=True)

    message = fields.Char(string='Message')

    probe_template_id = fields.Many2one(
        comodel_name='oversight.probe.template', required=True)
