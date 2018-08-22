# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Oversight',
    'summary': "Add Oversight Tools",
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/menu.xml',
        'views/view_oversight_check.xml',
        'views/view_oversight_probe_ssh_key.xml',
        'views/view_oversight_probe_template.xml',
        'views/view_oversight_probe_variant_disk_usage.xml',
        'views/view_oversight_probe_variant_http_code.xml',
        'views/view_oversight_probe_variant_ping.xml',
        'views/view_oversight_probe_variant_reminder.xml',
        'views/view_oversight_probe_variant_whois_expiration_jwa.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/oversight_probe_variant_http_code.xml',
        'demo/oversight_probe_variant_ping.xml',
        'demo/oversight_probe_variant_reminder.xml',
        'demo/oversight_probe_variant_whois_expiration_jwa.xml',
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [
            'paramiko',
        ],
    },
    'installable': True,
}
