# Copyright 2022 Sharuzzaman Ahmat Raslan <sharuzzaman@gmail.com>
# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import socket
import ssl

from cryptography import x509

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ProbeMixinCertificate(models.AbstractModel):
    _name = "probe.mixin.certificate"
    _inherit = ["mail.thread", "mail.activity.mixin", "probe.mixin"]
    _description = "Probe Mixin Certificate"

    certificate_ssl_tls_version = fields.Char(readonly=True)

    certificate_expire_datetime = fields.Datetime(readonly=True, tracking=True)

    certificate_day_before_expiration = fields.Integer(
        compute="_compute_certificate_day_before_expiration"
    )

    certificate_probe_state = fields.Selection(
        compute="_compute_certificate_probe_state",
        selection=lambda x: x._PROBE_STATE_SELECTION,
    )

    certificate_probe_last_state = fields.Selection(
        readonly=True,
        selection=lambda x: x._PROBE_LAST_STATE_SELECTION,
        default="01_probe_undefined",
        tracking=True,
    )

    certificate_warning_threshold = fields.Integer()

    certificate_probe_last_error_message = fields.Text(readonly=True)

    @api.depends("certificate_expire_datetime")
    def _compute_certificate_day_before_expiration(self):
        for url in self.filtered(lambda x: x.certificate_expire_datetime):
            url.certificate_day_before_expiration = (
                url.certificate_expire_datetime - fields.datetime.now()
            ).days
        for url in self.filtered(lambda x: not x.certificate_expire_datetime):
            url.certificate_day_before_expiration = 0

    @api.depends("certificate_expire_datetime", "certificate_probe_last_state")
    def _compute_certificate_probe_state(self):
        icp = self.env["ir.config_parameter"].sudo()
        for certificate in self:
            warning_limit = certificate.certificate_warning_threshold
            if not warning_limit:
                warning_limit = int(
                    icp.get_param("oversight.certificate_warning_threshold")
                )
            if certificate.certificate_probe_last_state == "01_probe_undefined":
                certificate.certificate_probe_state = "probe_undefined"
            elif certificate.certificate_day_before_expiration > warning_limit:
                certificate.certificate_probe_state = "success"
            elif (
                certificate.certificate_day_before_expiration < warning_limit
                and certificate.certificate_day_before_expiration > 0
            ):
                certificate.certificate_probe_state = "warning"
            else:
                certificate.certificate_probe_state = "error"

    def _probe_certificate_get_information(self):
        for index, certificate in enumerate(self, start=1):
            _logger.info(
                f"{index}/{len(self)}"
                f" - Updating Certification Information of {certificate.name} ..."
            )
            try:
                # See: https://stackoverflow.com/a/71153638
                # create default context
                _context = ssl.create_default_context()

                # override context so that it can get expired cert
                _context.check_hostname = False
                _context.verify_mode = ssl.CERT_NONE

                with socket.create_connection((certificate.name, 443)) as sock:
                    with _context.wrap_socket(
                        sock, server_hostname=certificate.name
                    ) as ssock:
                        # get cert in DER format
                        data = ssock.getpeercert(True)

                        # convert cert to PEM format
                        pem_data = ssl.DER_cert_to_PEM_cert(data)

                        # pem_data in string. convert to bytes using str.encode()
                        # extract cert info from PEM format
                        cert_data = x509.load_pem_x509_certificate(str.encode(pem_data))

                        # Note: For obscur reason, on CI, 'not_valid_after_utc'
                        # function is not available
                        # In that case, we so use the depreated not_valid_after function
                        if hasattr(cert_data, "not_valid_after_utc"):
                            expire_datetime = cert_data.not_valid_after_utc.replace(
                                tzinfo=None
                            )
                        else:
                            expire_datetime = cert_data.not_valid_after
                        ssl_tls_version = ssock.version()

            except socket.gaierror:
                message = _(
                    "socket.gaierror: URL '%(url)s' not found.", url=certificate.name
                )
                certificate._handle_probe_error(message, "certificate")
                continue
            except ConnectionRefusedError:
                message = _(
                    "ConnectionRefusedError: Certificate Not found on '%(url)s'.",
                    url=certificate.name,
                )
                certificate._handle_probe_error(message, "certificate")
                continue
            except ssl.SSLEOFError:
                message = _(
                    "SSLEOFError: Unable to get certificate of '%(url)s'.",
                    url=certificate.name,
                )
                certificate._handle_probe_error(message, "certificate")
                continue
            except ssl.SSLError:
                message = _(
                    "SSLError: Unable to get certificate of '%(url)s'.",
                    url=certificate.name,
                )
                certificate._handle_probe_error(message, "certificate")
                continue

            vals = {
                "certificate_ssl_tls_version": ssl_tls_version,
                "certificate_expire_datetime": expire_datetime,
            }

            certificate._handle_probe_ok(vals, "certificate")
