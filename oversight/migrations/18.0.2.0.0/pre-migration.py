from openupgradelib import openupgrade

_RENAME_COLUMNS = {
    "oversight_domain_name": [
        ("domain_name", "name"),
        ("registrar", "registrar_name"),
        ("creation_datetime", "registrar_creation_datetime"),
        ("expire_datetime", "registrar_expire_datetime"),
        ("day_before_expiration", "registrar_day_before_expiration"),
    ],
    "oversight_url": [
        ("url", "name"),
        ("ssl_tls_version", "certificate_ssl_tls_version"),
        ("expire_datetime", "certificate_expire_datetime"),
        ("day_before_expiration", "certificate_day_before_expiration"),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    for table_name, field_definitions in _RENAME_COLUMNS.items():
        for old_field_name, new_field_name in field_definitions:
            if openupgrade.column_exists(env.cr, table_name, old_field_name):
                openupgrade.rename_columns(
                    env.cr,
                    {table_name: [(old_field_name, new_field_name)]},
                )
