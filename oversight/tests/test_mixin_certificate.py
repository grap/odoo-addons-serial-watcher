# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMixinCertificate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_certificate_correct_domain(self):
        url = self.env["oversight.url"].create({"name": "www.les-scop.coop"})
        self.assertFalse(url.certificate_ssl_tls_version)
        self.assertEqual(url.certificate_day_before_expiration, 0)
        self.assertEqual(url.certificate_probe_last_state, "01_probe_undefined")
        self.assertEqual(url.certificate_probe_state, "probe_undefined")

        url.button_update_cert_info()

        self.assertTrue(url.certificate_ssl_tls_version)
        self.assertGreater(url.certificate_day_before_expiration, 0)
        self.assertEqual(url.certificate_probe_last_state, "03_probe_ok")

        self.env["ir.config_parameter"].set_param(
            "oversight.certificate_warning_threshold", 10000
        )
        url._compute_certificate_probe_state()
        self.assertEqual(url.certificate_probe_state, "warning")

    def test_registrar_incorrect_domain(self):
        url = self.env["oversight.url"].create({"name": "www.total-basf.coop"})

        self.assertFalse(url.certificate_ssl_tls_version)

        url.button_update_cert_info()

        self.assertFalse(url.certificate_ssl_tls_version)
