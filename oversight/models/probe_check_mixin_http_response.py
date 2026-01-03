# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

import requests

from odoo import fields, models

from .probe_result import _PROBE_CHECK_STATE_SELECTION

_logger = logging.getLogger(__name__)


class ProbeCheckMixinHttpResponse(models.AbstractModel):
    _name = "probe.mixin.http.response"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.check.mixin"]
    _description = "Probe Check Mixin Http Response"

    http_response_active = fields.Boolean(default=True, tracking=True)

    http_response_qty = fields.Integer(
        "Result Count", compute="_compute_http_response_qty"
    )

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
                    f"{index}/{len(self)}"
                    f" - SKIP HTTP Call for the url {http_response.name} ..."
                )
                continue

            _logger.info(
                f"{index}/{len(self)}"
                f" - Make HTTP Call and wait response for the url {http_response.name} ..."
            )
            # try:
            if True:
                result = requests.get(f"https://{http_response.name}", timeout=1)

                if result.status_code == 200:
                    http_response._handle_probe_ok("http_response")
                    continue
                error_message = f"Bad Status Code: {result.status_code}"
            # except requests.exceptions.ConnectionError as exception:
            #     import pdb

            #     pdb.set_trace()
            #     error_message = "Timeout Expired."
            # except Exception as exception:
            #     import pdb

            #     pdb.set_trace()
            #     error_message = "Unknown error."

            # http_response._handle_probe_error(
            #     "http_response", error_message=error_message
            # )
