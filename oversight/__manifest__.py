# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Oversight",
    "summary": "Oversight Tools",
    "version": "18.0.2.0.0",
    "category": "Tools",
    "author": "GRAP",
    "website": "https://github.com/grap/odoo-addons-serial-watcher",
    "license": "AGPL-3",
    "depends": [
        # Odoo
        "mail",
        # OCA
        "web_notify",
    ],
    "data": [
        "security/ir_module_category.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
        "data/mail_template.xml",
        "views/view_oversight_domain_name.xml",
        "views/view_oversight_url.xml",
        "views/view_oversight_server.xml",
        "wizards/view_res_config_settings.xml",
        # "views/view_oversight_ssh_authentication.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo_oversight_domain_name.xml",
        "demo/demo_oversight_url.xml",
    ],
    "external_dependencies": {
        "bin": ["whois"],
        # special definition used by OCA to install packages
        "deb": ["whois"],
    },
}
