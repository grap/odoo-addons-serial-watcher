# Copyright 2022 Sharuzzaman Ahmat Raslan <sharuzzaman@gmail.com>
# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class ProbeMixin(models.AbstractModel):
    _name = "probe.mixin"
    _description = "Probe Mixin"

    _PROBE_STATE_SELECTION = [
        ("probe_undefined", "Undefined"),
        ("error", "Error"),
        ("warning", "Warning"),
        ("success", "Success"),
    ]

    _PROBE_LAST_STATE_SELECTION = [
        ("01_probe_undefined", "Undefined"),
        ("02_probe_failed", "Error"),
        ("03_probe_ok", "OK"),
    ]

    def _handle_probe_error(self, message, probe_name, data=False):
        self.ensure_one()
        _logger.error(message)
        self.env.user.notify_danger(message)
        if data:
            full_message = _(
                "Message: %(message)s\n\nData:\n%(data)s", message=message, data=data
            )
        else:
            full_message = _("Message: %(message)s", message=message)

        self.write(
            {
                f"{probe_name}_probe_last_state": "02_probe_failed",
                f"{probe_name}_probe_last_error_message": full_message,
            }
        )

    def _handle_probe_ok(self, vals, probe_name):
        self.ensure_one()
        vals.update(
            {
                f"{probe_name}_probe_last_state": "03_probe_ok",
                f"{probe_name}_probe_last_error_message": False,
            }
        )
        new_vals = {
            x: vals.get(x) for x in vals.keys() if vals.get(x) != getattr(self, x)
        }

        if new_vals:
            _logger.info(f"New Information for {self.name}: {new_vals}.")
            self.write(vals)

    @api.model
    def _search_probe_state(self, probe_name, operator, value):
        if operator == "!=":
            items = self.search([]).filtered(
                lambda x: getattr(x, f"{probe_name}_probe_state") != value
            )
        elif operator == "not in":
            items = self.search([]).filtered(
                lambda x: getattr(x, f"{probe_name}_probe_state") not in value
            )
        elif operator == "=":
            items = self.search([]).filtered(
                lambda x: getattr(x, f"{probe_name}_probe_state") == value
            )
        elif operator == "in":
            items = self.search([]).filtered(
                lambda x: getattr(x, f"{probe_name}_probe_state") in value
            )
        else:
            raise NotImplementedError(
                _("Not implemented operator '%(operator)s'", operator=operator)
            )
        return [("id", "in", items.ids)]
