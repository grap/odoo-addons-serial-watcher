# Copyright 2022 Sharuzzaman Ahmat Raslan <sharuzzaman@gmail.com>
# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import socket
import ssl

from cryptography import x509

from odoo import api, fields, models


class OversightUrl(models.Model):
    _name = "oversight.url"
    _description = "URL"
    _rec_name = "url"

    url = fields.Char(required=True)

    domain_name_id = fields.Many2one(
        compute="_compute_domain_name_id",
        store=True,
        comodel_name="oversight.domain.name",
        ondelete="restrict",
    )

    ssl_tls_version = fields.Char(readonly=True)

    expire_datetime = fields.Datetime(readonly=True)

    server_id = fields.Many2one(
        compute="_compute_server_id",
        store=True,
        comodel_name="oversight.server",
        ondelete="restrict",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "url" in vals:
                vals["url"] = self._clean_url(vals["url"])
        return super().create(vals_list)

    @api.model
    def _clean_url(self, url):
        if not url:
            return False
        while url.endswith("/"):
            url = url[:-1]
        url = url.replace("http://", "").replace("https://", "")
        return url

    @api.depends("url")
    def _compute_domain_name_id(self):
        OversightDomainName = self.env["oversight.domain.name"]
        for url in self:
            if not self._clean_url(url.url) or "." not in self._clean_url(url.url):
                url.domain_name_id = False
                continue
            domain = ".".join(self._clean_url(url.url).split(".")[-2:])

            domain_name = OversightDomainName.search(
                [("domain_name", "=", domain)], limit=1
            )
            if not domain_name:
                domain_name = OversightDomainName.create({"domain_name": domain})
            url.domain_name_id = domain_name

    @api.depends("url")
    def _compute_server_id(self):
        OversightServer = self.env["oversight.server"]
        for url in self:
            if not self._clean_url(url.url) or "." not in self._clean_url(url.url):
                url.server_id = False
                continue
            try:
                ip = socket.gethostbyname(self._clean_url(url.url))
                server = OversightServer.search([("ip", "=", ip)], limit=1)
                if not server:
                    server = OversightServer.create({"ip": ip})
                url.server_id = server
            except socket.gaierror:
                url.server_id = False
                continue

    def button_update_cert_info(self):
        for url in self:
            # See: https://stackoverflow.com/a/71153638
            # create default context
            context = ssl.create_default_context()

            # override context so that it can get expired cert
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((url.url, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=url.url) as ssock:
                    # get cert in DER format
                    data = ssock.getpeercert(True)

                    # convert cert to PEM format
                    pem_data = ssl.DER_cert_to_PEM_cert(data)

                    # pem_data in string. convert to bytes using str.encode()
                    # extract cert info from PEM format
                    cert_data = x509.load_pem_x509_certificate(str.encode(pem_data))
                    url.write(
                        {
                            "ssl_tls_version": ssock.version(),
                            "expire_datetime": cert_data.not_valid_after_utc.replace(
                                tzinfo=None
                            ),
                        }
                    )
