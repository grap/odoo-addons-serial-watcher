# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OversightProbeSshKey(models.Model):
    _name = 'oversight.probe.ssh.key'
    _order = 'name'

    name = fields.Char(required=True)

    path = fields.Char(required=True)
