# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestOverSightServer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_service = cls.env.ref("oversight.oversight_service_website")

    def test_server_name(self):
        # Check that the url is well cleaned
        new_url = self.env["oversight.url"].create(
            {"name": "www.les-scop.coop", "service_id": self.demo_service.id}
        )

        # Verify that a server has been created
        server = new_url.server_id
        self.assertTrue(server)

        # Check the name of the server
        ip = server.ip
        self.assertEqual(server.name, ip)

        # add a technical name and check again server name
        server.technical_name = "SCOP"
        self.assertEqual(server.name, f"SCOP ({ip})")
