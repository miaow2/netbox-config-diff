from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('netbox_config_diff', '0004_update_script'),
    ]

    operations = [
        migrations.AddField(
            model_name='configcompliance',
            name='extra',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='configcompliance',
            name='missing',
            field=models.TextField(blank=True),
        ),
    ]
