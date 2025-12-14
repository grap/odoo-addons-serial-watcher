# Copyright (C) 2025 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


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

    @api.depends("url")
    def _compute_domain_name_id(self):
        OversightDomainName = self.env["oversight.domain.name"]
        for url in self:
            if not url.url or "." not in url.url:
                url.domain_name_id = False
                continue
            domain = ".".join(url.url.split(".")[-2:])

            domain_name = OversightDomainName.search(
                [("domain_name", "=", domain)], limit=1
            )
            if not domain_name:
                domain_name = OversightDomainName.create({"domain_name": domain})
            url.domain_name_id = domain_name
