# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProbeCheckMixin(models.AbstractModel):
    _name = "probe.check.mixin"
    _description = "Probe Check Mixin"

    def _probe_check_active(self):
        # TODO: implement here, time check
        return True

    def _compute_result_qty(self, probe_name):
        read_group_var = self.env["probe.result"]._read_group(
            [
                ("res_id", "in", self.ids),
                ("res_model", "=", self._name),
                ("probe_name", "=", probe_name),
            ],
            groupby=["res_id"],
            aggregates=["__count"],
        )

        return dict(read_group_var)

    def _handle_probe_ok(self, probe_name):
        self.ensure_one()
        message = f"Probe {probe_name}. State OK."
        _logger.info("message")
        self.env.user.notify_success(message)
        self._handle_probe(probe_name, "03_ok")

    def _handle_probe_error(self, probe_name, error_message=False):
        self.ensure_one()
        message = f"Probe {probe_name}. State KO. {error_message}"
        _logger.info(message)
        self.env.user.notify_danger(message)
        self._handle_probe(probe_name, "02_ko", error_message=error_message)

    def _handle_probe(self, probe_name, state, error_message=False):
        self.ensure_one()
        self.env["probe.result"].create(
            {
                "res_model": self._name,
                "res_id": self.id,
                "probe_name": probe_name,
                "state": state,
                "probe_datetime": fields.Datetime.now(),
                "error_message": error_message,
            }
        )
        state_field = f"{probe_name}_state"
        current_state = getattr(self, state_field)
        error_message_field = f"{probe_name}_error_message"
        current_error_message = getattr(self, error_message_field)
        vals = {}
        if state != current_state:
            vals.update({state_field: state})
        if error_message != current_error_message:
            vals.update({error_message_field: error_message})
        if vals:
            self.write(vals)
