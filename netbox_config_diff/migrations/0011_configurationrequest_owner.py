import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_config_diff', '0010_create_script'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationrequest',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'),
        ),
    ]
