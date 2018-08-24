# coding: utf-8
# Copyright (C) 2018 -  Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import paramiko
except ImportError as err:
    _logger.info(err)


class OversightProbeSSHMixin(models.AbstractModel):
    _name = 'oversight.probe.ssh.mixin'

    server = fields.Char(required=True)

    login = fields.Char(required=True)

    password = fields.Char(required=False)

    ssh_key_id = fields.Many2one(
        comodel_name='oversight.probe.ssh.key', string='SSH Private Key')

    @api.multi
    def _ssh_execute(self, command):
        self.ensure_one()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.ssh_key_id:
            key = paramiko.RSAKey.from_private_key_file(self.ssh_key_id.path)

        if self.password and self.ssh_key_id:
            ssh.connect(
                self.server,
                username=self.login,
                password=self.password,
                pkey=key)
        elif self.password:
            ssh.connect(
                self.server,
                username=self.login,
                password=self.password)
        else:
            ssh.connect(
                self.server,
                username=self.login,
                pkey=key)
        stdin, stdout, stderr = ssh.exec_command(command)
        res = stdout.readlines()
        ssh.close()
        return res
