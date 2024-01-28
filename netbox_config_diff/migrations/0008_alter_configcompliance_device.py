from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0181_rename_device_role_device_role"),
        ("netbox_config_diff", "0007_configurationrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configcompliance",
            name="device",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="config_compliance",
                to="dcim.device",
            ),
        ),
    ]
