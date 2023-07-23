import os

from django.conf import settings
from django.db import migrations
from pathlib import Path

SCRIPT_NAME = "config_diff.py"


def forward_func(apps, schema_editor):
    script_path = Path(__file__).parent.parent.joinpath("scripts", SCRIPT_NAME)
    new_path = os.path.join(settings.SCRIPTS_ROOT, SCRIPT_NAME)
    with open(script_path, "r") as script_file, open(new_path, "w") as new_file:
        new_file.write(script_file.read())


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """
    This is little hack if you install plugin before appearance of 0003 migration.
    Make custom script more dynamic, so I can change script logic in plugin without updating script.
    """
    dependencies = [
        ('netbox_config_diff', '0003_configcompliance_actual_config_and_more'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
