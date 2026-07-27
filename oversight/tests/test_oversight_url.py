# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestOverSightUrl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_service = cls.env.ref("oversight.oversight_service_website")

    def test_correct_url(self):
        # Check that the url is well cleaned
        new_url = self.env["oversight.url"].create(
            {"name": "https://www.les-scop.coop/", "service_id": self.demo_service.id}
        )
        self.assertEqual(new_url.name, "www.les-scop.coop")

        # Verify that a domain is created
        self.assertTrue(new_url.domain_name_id)

        # Verify the name of the domain
        self.assertEqual(new_url.domain_name_id.name, "les-scop.coop")

        # Verify that a server has been created
        self.assertTrue(new_url.server_id)

    def test_incorrect_url(self):
        # Check that the url is well cleaned
        new_url = self.env["oversight.url"].create(
            {"name": "NOT A VALID URL", "service_id": self.demo_service.id}
        )
        # Verify that a domain has NOT been created
        self.assertFalse(new_url.domain_name_id)

        # Verify that a server has NOT been created
        self.assertFalse(new_url.server_id)

    def test_unexisting_url(self):
        # Check that the url is well cleaned
        new_url = self.env["oversight.url"].create(
            {
                "name": "https://xxx.not-an-existing-url.bidouille/",
                "service_id": self.demo_service.id,
            }
        )
        self.assertEqual(new_url.name, "xxx.not-an-existing-url.bidouille")

        # Verify that a domain is created
        self.assertTrue(new_url.domain_name_id)

        # Verify the name of the domain
        self.assertEqual(new_url.domain_name_id.name, "not-an-existing-url.bidouille")

        # Verify that a server has NOT been created
        self.assertFalse(new_url.server_id)
