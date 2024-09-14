from django.db import migrations

from extras.models import Script, ScriptModule
from netbox.settings import VERSION


def forward_func(apps, schema_editor):
    if VERSION.startswith("3."):
        return

    if Script.objects.filter(name="ConfigDiffScript"):
        return

    obj = None
    for module in ScriptModule.objects.all():
        if module.python_name == "config_diff":
            obj = module
            break

    if obj:
        Script.objects.create(module=obj, name="ConfigDiffScript")


def reverse_func(apps, schema_editor):
    if VERSION.startswith("3."):
        return

    if qs := Script.objects.filter(name="ConfigDiffScript"):
        qs.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_config_diff", "0009_configcompliance_patch"),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
