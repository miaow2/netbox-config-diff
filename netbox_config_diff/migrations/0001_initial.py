from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('extras', '0092_delete_jobresult'),
        ('dcim', '0172_larger_power_draw_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('driver', models.CharField(max_length=25)),
                ('command', models.CharField(max_length=50)),
                ('exclude_regex', models.TextField(blank=True)),
                (
                    'platform',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name='platform_setting', to='dcim.platform'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('driver',),
            },
        ),
        migrations.CreateModel(
            name='ConfigCompliance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('status', models.CharField(default='pending', max_length=50)),
                ('diff', models.TextField(blank=True)),
                ('error', models.TextField(blank=True)),
                (
                    'device',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name='config_compliamce', to='dcim.device'
                    ),
                ),
            ],
            options={
                'ordering': ('device',),
            },
        ),
    ]
