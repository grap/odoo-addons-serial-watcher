# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class OversightProbeVariantMixin(models.AbstractModel):
    _name = "oversight.probe.variant.mixin"
    _description = "Oversight Probe Variant Mixin"
    _inherits = {"oversight.probe.template": "probe_template_id"}

    _variant_value_type = "none"
    _variant_probe_type = "none"

    probe_template_id = fields.Many2one(
        comodel_name="oversight.probe.template",
        required=True,
        ondelete="cascade",
        index=True,
        auto_join=True,
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({"probe_type": self._variant_probe_type})
        return res

    def button_execute_variant(self):
        return self.mapped("probe_template_id").button_execute_template()

    def button_enable_variant(self):
        return self.mapped("probe_template_id").button_enable_template()

    def button_disable_variant(self):
        return self.mapped("probe_template_id").button_disable_template()

    def copy(self, default=None):
        self.ensure_one()
        default = default and default or {}
        default["name"] = _("%s (copy)") % self.name
        return super().copy(default=default)
