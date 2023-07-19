import os

from core.choices import ManagedFileRootPathChoices
from django.conf import settings
from django.db import migrations
from pathlib import Path

SCRIPT_NAME = "config_diff.py"


def forward_func(apps, schema_editor):
    script_path = Path(__file__).parent.parent.joinpath("scripts", SCRIPT_NAME)
    new_path = os.path.join(settings.SCRIPTS_ROOT, SCRIPT_NAME)
    with open(script_path, "r") as script_file, open(new_path, "w") as new_file:
        new_file.write(script_file.read())

    ManagedFile = apps.get_model("core", "ManagedFile")
    db_alias = schema_editor.connection.alias

    ManagedFile.objects.using(db_alias).create(
        file_root=ManagedFileRootPathChoices.SCRIPTS,
        file_path=SCRIPT_NAME,
    )


def reverse_func(apps, schema_editor):
    ManagedFile = apps.get_model("core", "ManagedFile")
    db_alias = schema_editor.connection.alias

    ManagedFile.objects.using(db_alias).filter(
        file_root=ManagedFileRootPathChoices.SCRIPTS,
        file_path=SCRIPT_NAME,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('netbox_config_diff', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
