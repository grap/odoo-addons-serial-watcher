# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

_PROBE_CHECK_STATE_SELECTION = [
    ("01_unknown", "Unknown"),
    ("02_ko", "KO"),
    ("03_ok", "OK"),
]


class ProbeResult(models.Model):
    _name = "probe.result"
    _description = "Probe Result"
    _order = "probe_datetime desc, state"

    res_name = fields.Char("Resource Name", compute="_compute_res_name")

    res_model = fields.Char("Resource Model", readonly=True, required=True)

    res_id = fields.Many2oneReference(
        "Resource ID",
        readonly=True,
        model_field="res_model",
        required=True,
    )

    probe_name = fields.Selection(
        [
            ("ping", "Ping"),
            ("http_response", "HTTP Response"),
        ],
        readonly=True,
        required=True,
    )

    state = fields.Selection(
        selection=_PROBE_CHECK_STATE_SELECTION,
        readonly=True,
        required=True,
    )

    probe_datetime = fields.Datetime(readonly=True, required=True)

    error_message = fields.Char(readonly=True)

    def _compute_res_name(self):
        for attachment in self:
            if attachment.res_model and attachment.res_id:
                record = self.env[attachment.res_model].browse(attachment.res_id)
                attachment.res_name = record.display_name
            else:
                attachment.res_name = False
