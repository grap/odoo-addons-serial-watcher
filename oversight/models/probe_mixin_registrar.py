# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
import subprocess

from dateutil.parser import parse

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

_REGISTRAR_REGEX = {
    "registrar_name": [
        r"Registrar:\s?(.*)",
        r"registrar:\s?(.*)",
    ],
    "registrar_creation_datetime": [
        r"Creation Date:\s?(.*)",
        r"created:\s?(.*)",
    ],
    "registrar_expire_datetime": [
        r"Expiry Date:\s?(.*)",
        r"Expiration Date:\s?(.*)",
        r"Registry Expiry Date:\s?(.*)",
    ],
}


class ProbeMixinRegistrar(models.AbstractModel):
    _name = "probe.mixin.registrar"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.mixin"]
    _description = "Probe Mixin Registrar"

    registrar_name = fields.Char(readonly=True, tracking=True)

    registrar_creation_datetime = fields.Datetime(readonly=True, tracking=True)

    registrar_expire_datetime = fields.Datetime(readonly=True, tracking=True)

    registrar_probe_state = fields.Selection(
        compute="_compute_registrar_probe_state",
        selection=lambda x: x._PROBE_STATE_SELECTION,
    )

    registrar_probe_last_state = fields.Selection(
        readonly=True,
        selection=lambda x: x._PROBE_LAST_STATE_SELECTION,
        default="01_probe_undefined",
        tracking=True,
    )

    registrar_warning_threshold = fields.Integer()

    registrar_probe_last_error_message = fields.Text(readonly=True)

    registrar_day_before_expiration = fields.Integer(
        compute="_compute_registrar_day_before_expiration"
    )

    @api.depends("registrar_expire_datetime")
    def _compute_registrar_day_before_expiration(self):
        for registrar in self.filtered(lambda x: x.registrar_expire_datetime):
            registrar.registrar_day_before_expiration = (
                registrar.registrar_expire_datetime - fields.datetime.now()
            ).days
        for registrar in self.filtered(lambda x: not x.registrar_expire_datetime):
            registrar.registrar_day_before_expiration = 0

    @api.depends("registrar_expire_datetime", "registrar_probe_last_state")
    def _compute_registrar_probe_state(self):
        icp = self.env["ir.config_parameter"].sudo()
        for registrar in self:
            warning_limit = registrar.registrar_warning_threshold
            if not warning_limit:
                warning_limit = int(
                    icp.get_param("oversight.registrar_warning_threshold")
                )
            if registrar.registrar_probe_last_state == "01_probe_undefined":
                registrar.registrar_probe_state = "probe_undefined"
            elif registrar.registrar_day_before_expiration > warning_limit:
                registrar.registrar_probe_state = "success"
            elif (
                registrar.registrar_day_before_expiration < warning_limit
                and registrar.registrar_day_before_expiration > 0
            ):
                registrar.registrar_probe_state = "warning"
            else:
                registrar.registrar_probe_state = "error"

    def _probe_registrar_get_information(self):
        for index, registrar in enumerate(self, start=1):
            _logger.info(
                f"{index}/{len(self)}"
                f" - Updating Registrar Information of {registrar.name} ..."
            )
            vals = {}
            try:
                raw_result = subprocess.check_output(
                    ["whois", registrar.name], stderr=subprocess.STDOUT, timeout=60
                ).decode(errors="ignore")
            except subprocess.CalledProcessError as err:
                registrar._handle_probe_error(err.stdout.decode(), "registrar")
                continue

            for field_name, regex_values in _REGISTRAR_REGEX.items():
                for regex_value in regex_values:
                    result = re.findall(regex_value, raw_result)
                    if not result:
                        continue
                    if field_name.endswith("_datetime"):
                        vals[field_name] = parse(min(result)).replace(tzinfo=None)
                    else:
                        vals[field_name] = min(result).strip()

            # Verify that parsing worked
            if len(vals) != len(_REGISTRAR_REGEX):
                message = _(
                    "Unable to recover registrar Information"
                    " for the Domain Name '%(domain_name)s'. Values found: %(values)s",
                    domain_name=registrar.name,
                    values=vals,
                )
                registrar._handle_probe_error(message, "registrar", data=raw_result)
                continue

            registrar._handle_probe_ok(vals, "registrar")
