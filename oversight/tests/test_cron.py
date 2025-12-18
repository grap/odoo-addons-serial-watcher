# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCron(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_cron_registrar(self):
        self.env["oversight.domain.name"].cron_update_registrar_info()

    def test_cron_certificate(self):
        self.env["oversight.url"].cron_update_cert_info()
