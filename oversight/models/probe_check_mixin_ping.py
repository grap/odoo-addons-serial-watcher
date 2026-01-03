# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import subprocess

from odoo import fields, models

from .probe_result import _PROBE_CHECK_STATE_SELECTION

_logger = logging.getLogger(__name__)


class ProbeCheckMixinPing(models.AbstractModel):
    _name = "probe.mixin.ping"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.check.mixin"]
    _description = "Probe Check Mixin Ping"

    ping_active = fields.Boolean(default=True, tracking=True)

    ping_qty = fields.Integer("Result Count", compute="_compute_ping_qty")

    ping_state = fields.Selection(
        selection=_PROBE_CHECK_STATE_SELECTION,
        readonly=True,
        default="01_unknown",
        tracking=True,
    )

    ping_error_message = fields.Char(readonly=True, tracking=True)

    def _probe_ping_check(self):
        for index, ping in enumerate(self, start=1):
            if not ping._probe_check_active("ping"):
                _logger.info(
                    f"{index}/{len(self)}"
                    f" - SKIP ping Check for the server {ping.name} ({ping.ip})."
                )
                continue

            _logger.info(
                f"{index}/{len(self)}" f" - Pinging server {ping.name} ({ping.ip}) ..."
            )
            # https://stackoverflow.com/a/32684938
            command = ["ping", "-c", "1", ping.ip]
            try:
                result = subprocess.call(command, timeout=1)

                if result == 0:
                    ping._handle_probe_ok("ping")
                    continue
                error_message = "Unreachable Server."
            except subprocess.TimeoutExpired:
                error_message = "Timeout Expired."
            except Exception:
                error_message = "Unknown error."

            ping._handle_probe_error("ping", error_message=error_message)
