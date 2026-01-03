# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import subprocess

from odoo import fields, models

_logger = logging.getLogger(__name__)
from .probe_result import _PROBE_CHECK_STATE_SELECTION


class ProbeCheckMixinHttpResponse(models.AbstractModel):
    _name = "probe.mixin.http.response"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.check.mixin"]
    _description = "Probe Check Mixin Http Response"

    http_response_active = fields.Boolean(default=True, tracking=True)

    http_response_qty = fields.Integer("Result Count", compute="_compute_http_response_qty")

    http_response_state = fields.Selection(
        selection=_PROBE_CHECK_STATE_SELECTION,
        readonly=True,
        default="01_unknown",
        tracking=True,
    )

    http_response_error_message = fields.Char(readonly=True, tracking=True)

    def _probe_http_response_check(self):
        for index, http_response in enumerate(self, start=1):
            if not http_response._probe_check_active("http_response"):
                _logger.info(
                    f"{index}/{len(self)}" f" - SKIP HTTP Call for the url {http_response.name} ..."
                )
                continue

            _logger.info(
                f"{index}/{len(self)}" f" - Make HTTP Call and wait response for the url {http_response.name} ..."
            )
            # https://stackoverflow.com/a/32684938
            command = ["http_response", "-c", "1", http_response.ip]
            try:
                result = subprocess.call(command, timeout=1)

                if result == 0:
                    url._handle_probe_ok("http_response")
                    continue
                error_message = "Unreachable Server."
            except subprocess.TimeoutExpired:
                error_message = "Timeout Expired."
            except Exception:
                error_message = "Unknown error."

            url._handle_probe_error("http_response", error_message=error_message)
