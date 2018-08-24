# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


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

    date_start = fields.Datetime(required=True, readonly=True)

    date_start_string = fields.Char(
        compute='_compute_date_start_string', string='Date', store=True)

    state = fields.Selection(
        selection=_SELECTION_STATE, string='State', required=True,
        readonly=True)

    message = fields.Char(string='Message', readonly=True)

    probe_template_id = fields.Many2one(
        comodel_name='oversight.probe.template', required=True,
        readonly=True, ondelete='cascade')

    value_integer = fields.Integer(
        string='Value (Integer)', readonly=True)

    value_text = fields.Char(
        string='Value (Text)', readonly=True)

    value_float = fields.Float(
        string='Value (Float)', readonly=True, default=-1)

    @api.multi
    @api.depends('date_start')
    def _compute_date_start_string(self):
        for check in self:
            check.date_start_string = check.date_start
