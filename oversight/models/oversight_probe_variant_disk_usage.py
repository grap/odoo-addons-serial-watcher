# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class OversightProbeVariantDiskUsage(models.Model):
    _name = 'oversight.probe.variant.disk.usage'
    _inherit = [
        'oversight.probe.ssh.mixin',
        'oversight.probe.variant.mixin',
    ]

    _undefined_value = -1
    _variant_value_type = 'float'
    _variant_probe_type = 'disk.usage'

    disk = fields.Char(required=True)

    warning_threshold = fields.Float(required=True, default=60)

    error_threshold = fields.Float(required=True, default=90)

    # Overload Section
    @api.multi
    def _get_value_string(self, check):
        self.ensure_one()
        if check.value_float == self._undefined_value:
            return False
        else:
            return _('%.2f %%') % (check.value_float)

    @api.multi
    def _run_oversight_variant(self):
        self.ensure_one()
        message = False
        value_float = self._undefined_value
        try:
            res = self._ssh_execute('df %s' % self.disk)
            res = res[1].split(" ")
            res = [x for x in res if x]
            used_space = float(res[2])
            total_space = float(res[1])
            value_float = used_space / total_space * 100
            if value_float >= self.error_threshold:
                state = 'error'
            elif value_float >= self.warning_threshold:
                state = 'warning'
            else:
                state = 'info'
            message = "Used Space %s" % (value_float)
        except Exception as e:
            state = 'critical'
            message = e.message
        return {
            'state': state,
            'message': message,
            'value_float': value_float,
        }
