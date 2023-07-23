from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('netbox_config_diff', '0002_add_script'),
    ]

    operations = [
        migrations.AddField(
            model_name='configcompliance',
            name='actual_config',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='configcompliance',
            name='rendered_config',
            field=models.TextField(blank=True),
        ),
    ]
