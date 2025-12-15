# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
import subprocess

from dateutil.parser import parse

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OversightDomainName(models.Model):
    _name = "oversight.domain.name"
    _description = "Domain Name"
    _rec_name = "domain_name"

    domain_name = fields.Char(required=True)

    registrar = fields.Char(readonly=True)

    creation_datetime = fields.Datetime(readonly=True)

    expire_datetime = fields.Datetime(readonly=True)

    def button_update_registrar_info(self):
        infos = {
            "registrar": [r"Registrar:\s?(.*)", r"registrar:\s?(.*)"],
            "creation_datetime": [r"Creation Date:\s?(.*)", r"created:\s?(.*)"],
            "expire_datetime": [r"Expiry Date:\s?(.*)", r"Expiration Date:\s?(.*)"],
        }

        for index, domain_name in enumerate(self, start=1):
            _logger.info(
                f"{index}/{len(self)}"
                f" - Updating Registrar Information of {domain_name.domain_name} ..."
            )
            vals = {}
            with subprocess.Popen(
                ["whois", domain_name.domain_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ) as processHandle:
                raw_result = processHandle.communicate(timeout=10)[0].decode(
                    errors="ignore"
                )
            for field_name, regex_values in infos.items():
                for regex_value in regex_values:
                    result = re.findall(regex_value, raw_result)
                    if not result:
                        continue
                    if field_name.endswith("_datetime"):
                        vals[field_name] = parse(min(result)).replace(tzinfo=None)
                    else:
                        vals[field_name] = min(result)
            domain_name.write(vals)
