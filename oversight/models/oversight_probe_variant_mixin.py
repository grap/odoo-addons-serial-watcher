# coding: utf-8
# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class OversightProbeVariantMixin(models.AbstractModel):
    _name = 'oversight.probe.variant.mixin'
    _inherits = {'oversight.probe.template': 'probe_template_id'}

    _variant_value_type = 'none'
    _variant_probe_type = 'none'

    probe_template_id = fields.Many2one(
        comodel_name='oversight.probe.template', string='Probe Template',
        required=True, ondelete="cascade", select=True, auto_join=True)

    @api.model
    def default_get(self, fields):
        res = super(OversightProbeVariantMixin, self).default_get(fields)
        res.update({'probe_type': self._variant_probe_type})
        return res

    @api.multi
    def button_execute_variant(self):
        return self.mapped('probe_template_id').button_execute_template()

    @api.multi
    def button_confirm_variant(self):
        return self.mapped('probe_template_id').button_confirm_template()

    @api.multi
    def button_draft_variant(self):
        return self.mapped('probe_template_id').button_draft_template()
