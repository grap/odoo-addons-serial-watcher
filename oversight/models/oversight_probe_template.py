# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class OversightProbeTemplate(models.Model):
    _name = 'oversight.probe.template'
    _inherit = 'ir.needaction_mixin'
    _order = 'name'

    # Field Section
    _SELECTION_PROBE_TYPE = [
        ('ping', 'Ping'),
        ('http.code', 'HTTP Code'),
        ('disk.usage', 'Disk Usage'),
        ('whois.expiration.jwa', 'Whois Expiration (JWA)'),
        ('reminder', 'Reminder'),
    ]

    _SELECTION_INTERVAL_TYPE = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('work_days', 'Work Days'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]

    _SELECTION_LAST_CHECK_STATE = [
        ('not_set', 'Not Set'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    _SELECTION_VALUE_TYPE = [
        ('none', 'None'),
        ('float', 'Float'),
        ('text', 'Text'),
        ('integer', 'Integer'),
    ]

    active = fields.Boolean(default=False, copy=False, readonly=True)

    name = fields.Char(required=True)

    probe_type = fields.Selection(
        selection=_SELECTION_PROBE_TYPE, string='Type', required=True,
        readonly=True)

    cron_id = fields.Many2one(
        comodel_name='ir.cron', copy=False, readonly=True)

    interval_number = fields.Integer(
        string='Interval Number', default=1, required=True,
        help="Repeat every x.", )

    interval_type = fields.Selection(
        string='Interval Unit', selection=_SELECTION_INTERVAL_TYPE,
        default='minutes', required=True)

    image = fields.Binary()

    has_image = fields.Boolean(compute='_compute_has_image', store=True)

    check_ids = fields.One2many(
        string='Checks',
        comodel_name='oversight.check', inverse_name='probe_template_id')

    check_qty = fields.Integer(
        string='Checks Qty', compute='_compute_check_qty')

    last_check_id = fields.Many2one(
        comodel_name='oversight.check', string='Last Check', readonly=True,
        copy=False)

    last_check_state = fields.Selection(
        selection=_SELECTION_LAST_CHECK_STATE, string='Last Check State',
        readonly=True, compute='_compute_last_check', store=True)

    last_value_string = fields.Char(
        string='Last Value', compute='_compute_last_check', store=True)

    alert_ids = fields.One2many(
        comodel_name='oversight.probe.alert', string='Alerts',
        inverse_name='probe_template_id')

    color = fields.Integer(compute='_compute_color')

    value_type = fields.Selection(
        selection=_SELECTION_VALUE_TYPE, compute='_compute_value_type')

    # Compute section
    @api.multi
    @api.depends('last_check_id')
    def _compute_last_check(self):
        for template in self.filtered(lambda x: x.last_check_id):
            template.last_check_state = template.last_check_id.state
            template.last_value_string =\
                template._get_variant()._get_value_string(
                    template.last_check_id)
        for template in self.filtered(lambda x: not x.last_check_id):
            template.last_check_state = 'not_set'
            template.last_value_string = ''

    @api.multi
    @api.depends('image')
    def _compute_has_image(self):
        for template in self:
            template.has_image = template.image

    @api.multi
    def _compute_value_type(self):
        for template in self:
            template.value_type =\
                template._get_variant()._variant_value_type

    @api.multi
    def _compute_color(self):
        for template in self:
            if template.last_check_state == 'not_set':
                template.color = 0
            elif template.last_check_state == 'info':
                template.color = 5
            elif template.last_check_state == 'warning':
                template.color = 3
            elif template.last_check_state == 'error':
                template.color = 2
            elif template.last_check_state == 'critical':
                template.color = 1

    @api.multi
    def _compute_check_qty(self):
        for probe in self:
            probe.check_qty = len(probe.check_ids)

    # View Section
    @api.model
    def _needaction_domain_get(self):
        return [
            ('active', '=', True),
            ('last_check_state', 'in', ['warning', 'error', 'critical']),
        ]

    @api.multi
    def button_execute_template(self):
        for template in self:
            template._run_oversight_template()

    @api.multi
    def button_enable_template(self):
        cron_obj = self.env['ir.cron']
        for template in self.filtered(lambda x: not x.active):
            if not template.cron_id:
                template.cron_id = cron_obj.create(template._prepare_cron())
            else:
                template.cron_id.active = True
            template.active = True

    @api.multi
    def button_disable_template(self):
        for template in self.filtered(lambda x: x.active):
            template.cron_id.active = False
            template.active = False

    @api.multi
    def button_see_variant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Settings'),
            'res_model': self._get_variant_model()._name,
            'res_id': self._get_variant().id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
        }

    @api.model
    def cron_execute(self, ids):
        items = self.browse(ids)
        items._run_oversight_template()

    # Overload Section
    @api.multi
    def unlink(self):
        self.filtered(lambda x: x.cron_id).mapped('cron_id').unlink()
        self.mapped('last_check_id').unlink()
        return super(OversightProbeTemplate, self).unlink()

    # Private Section
    @api.multi
    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _('Probe %s') % (self.name),
            'user_id': SUPERUSER_ID,
            'model': 'oversight.probe.template',
            'function': 'cron_execute',
            'numbercall': -1,
            'args': repr(([self.id],)),
            'interval_number': self.interval_number,
            'interval_type': self.interval_type,
        }

    @api.multi
    def _get_variant_model(self):
        self.ensure_one()
        return self.env['oversight.probe.variant.%s' % self.probe_type]

    @api.multi
    def _get_variant(self):
        self.ensure_one()
        model_obj = self._get_variant_model()
        return model_obj.search([('probe_template_id', '=', self.id)])

    @api.multi
    def _run_oversight_template(self):
        check_obj = self.env['oversight.check']
        for probe in self:
            # Recover generic information
            check_value = {
                'date_start': datetime.now().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'probe_template_id': probe.id,
            }
            variant = probe._get_variant()
            check_value.update(variant._run_oversight_variant())
            check = check_obj.create(check_value)

            probe.write({
                'last_check_id': check.id,
            })

            # Handle Alert
            probe.alert_ids._handle_check(check)
