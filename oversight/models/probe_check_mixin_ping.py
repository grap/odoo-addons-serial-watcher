# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import subprocess

from odoo import models

_logger = logging.getLogger(__name__)


class ProbeCheckMixinPing(models.AbstractModel):
    _name = "probe.mixin.ping"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.check.mixin"]
    _description = "Probe Check Mixin Ping"

    def _probe_ping_check(self):
        if not self._probe_check_active():
            return
        for index, ping in enumerate(self, start=1):
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
