from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_config_diff", "0008_alter_configcompliance_device"),
    ]

    operations = [
        migrations.AddField(
            model_name="configcompliance",
            name="patch",
            field=models.TextField(blank=True),
        ),
    ]
