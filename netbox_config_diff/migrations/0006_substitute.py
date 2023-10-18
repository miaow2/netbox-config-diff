import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0098_webhook_custom_field_data_webhook_tags'),
        ('netbox_config_diff', '0005_configcompliance_extra_missing'),
    ]

    operations = [
        migrations.CreateModel(
            name='Substitute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=250,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                flags=re.RegexFlag['IGNORECASE'],
                                message='Only alphanumeric characters and underscores are allowed.',
                                regex='^[a-z0-9_]+$',
                            ),
                            django.core.validators.RegexValidator(
                                flags=re.RegexFlag['IGNORECASE'],
                                inverse_match=True,
                                message='Double underscores are not permitted in names.',
                                regex='__',
                            ),
                        ],
                    ),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('regexp', models.CharField(max_length=1000)),
                (
                    'platform_setting',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='substitutes',
                        to='netbox_config_diff.platformsetting',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
