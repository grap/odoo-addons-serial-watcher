# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
from requests.auth import HTTPBasicAuth

from odoo import models


class OversightProbeJsonMixin(models.AbstractModel):
    _name = "oversight.probe.json.mixin"

    # To Overload Section
    _json_auth_method = False
    _base_json_url = ""
    _json_required_keys = []

    def _prepare_full_url(self):
        return False

    # Custom Section

    def _json_execute(self):
        self.ensure_one()
        full_url = self._prepare_full_url()
        response = requests.get(full_url, auth=self._prepare_auth(), timeout=10)

        # check HTTP code

        if response.status_code == 401:
            raise Exception(f"Authentification failed for the call of {full_url}")
        elif response.status_code != 200:
            raise Exception(
                "Unexpected Status Code %d when calling %s"
                % (response.status_code, full_url)
            )

        # Check if all required keys are present
        result = response.json()
        for key in self._json_required_keys:
            if key not in result:
                raise Exception(
                    f"Key '{key}' not found when parsing"
                    f"the response of the URL {full_url}."
                    " Maybe API has changed."
                )
        return result

    def _prepare_auth(self):
        self.ensure_one()
        config_obj = self.env["ir.config_parameter"]

        if self._json_auth_method == "ir.config_parameter":
            login = config_obj.get_param(f"{self._name}.login", "False")
            password = config_obj.get_param(f"{self._name}.password", "False")
            return HTTPBasicAuth(login, password)
        else:
            return False
