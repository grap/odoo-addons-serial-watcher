# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Oversight",
    "summary": "Oversight Tools",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-serial-watcher",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        # "data/test.xml",
        "views/menu.xml",
        "views/view_oversight_domain_name.xml",
        "views/view_oversight_url.xml",
    ],
    "demo": [
        "demo/demo_oversight_domain_name.xml",
        "demo/demo_oversight_url.xml",
    ],
    "external_dependencies": {},
}
