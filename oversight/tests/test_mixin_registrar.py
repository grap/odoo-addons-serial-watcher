# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMixinRegistrar(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_registrar_correct_domain(self):
        domain = self.env["oversight.domain.name"].create({"name": "les-scop.coop"})
        self.assertFalse(domain.registrar_name)
        self.assertEqual(domain.registrar_day_before_expiration, 0)
        self.assertEqual(domain.registrar_probe_last_state, "01_probe_undefined")
        self.assertEqual(domain.registrar_probe_state, "probe_undefined")

        domain.button_update_registrar_info()

        self.assertTrue(domain.registrar_name)
        self.assertGreater(domain.registrar_day_before_expiration, 0)
        self.assertEqual(domain.registrar_probe_last_state, "03_probe_ok")
        self.assertEqual(domain.registrar_probe_state, "success")

        self.env["ir.config_parameter"].set_param(
            "oversight.registrar_warning_threshold", 10000
        )
        domain._compute_registrar_probe_state()
        self.assertEqual(domain.registrar_probe_state, "warning")

    def test_registrar_incorrect_domain(self):
        domain = self.env["oversight.domain.name"].create({"name": "total-basf.coop"})
        self.assertFalse(domain.registrar_name)
        self.assertEqual(domain.registrar_probe_last_state, "01_probe_undefined")

        domain.button_update_registrar_info()

        self.assertFalse(domain.registrar_name)
        self.assertEqual(domain.registrar_probe_last_state, "02_probe_failed")
