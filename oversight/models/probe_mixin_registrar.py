# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import logging

import whois

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
        # search="_search_registrar_probe_state",
        search=lambda self, *args: self._search_probe_state("registrar", *args),
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
            elif registrar.registrar_probe_last_state == "02_probe_failed":
                registrar.registrar_probe_state = "probe_failed"
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
                result = whois.whois(registrar.name)

                if not any(result.values()):
                    # In weird cases, no error is raised, if domain doesn't exist
                    #  and the result is just a dict with all null keys
                    # exemple : 'total-basf.coop'
                    # We consider error anyway.
                    registrar._handle_probe_error(
                        "Empty dictionnary return by whois", "registrar"
                    )
                    continue

                creation_date = expiration_date = False
                if type(result.creation_date) is datetime.datetime:
                    creation_date = result.creation_date
                elif type(result.creation_date) is list:
                    creation_date = max(result.creation_date)

                if type(result.expiration_date) is datetime.datetime:
                    expiration_date = result.expiration_date
                elif type(result.expiration_date) is list:
                    expiration_date = max(result.expiration_date)

                vals.update(
                    {
                        "registrar_name": result.registrar,
                        "registrar_creation_datetime": creation_date
                        and creation_date.replace(tzinfo=datetime.timezone.utc).replace(
                            tzinfo=None
                        ),
                        "registrar_expire_datetime": expiration_date
                        and expiration_date.replace(
                            tzinfo=datetime.timezone.utc
                        ).replace(tzinfo=None),
                    }
                )

            except (
                whois.exceptions.WhoisError,
                whois.exceptions.WhoisDomainNotFoundError,
            ) as err:
                registrar._handle_probe_error(err, "registrar")
                continue

            registrar._handle_probe_ok(vals, "registrar")
