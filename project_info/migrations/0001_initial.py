# Generated by Django 3.1.7 on 2021-07-08 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidProject',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=128, unique=True)),
                ('project_logo', models.FileField(default='imgs/project_info/Neulion.png', upload_to='imgs/project_info')),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='IosProject',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=128, unique=True)),
                ('project_logo', models.FileField(default='imgs/project_info/Neulion.png', upload_to='imgs/project_info')),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='IosBuild',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('project_version', models.CharField(max_length=128)),
                ('date', models.DateTimeField(auto_now=True)),
                ('x_framework', models.BooleanField()),
                ('framework', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_info.iosproject', to_field='project_name')),
            ],
        ),
        migrations.CreateModel(
            name='AndroidBuild',
            fields=[
                ('nid', models.AutoField(primary_key=True, serialize=False)),
                ('package_name', models.CharField(max_length=128)),
                ('package_version_name', models.CharField(max_length=128)),
                ('package_version_code', models.IntegerField()),
                ('module_name', models.CharField(max_length=128)),
                ('product_flavor_name', models.CharField(max_length=128)),
                ('package_target_sdk', models.IntegerField(null=True)),
                ('package_mini_sdk', models.IntegerField(null=True)),
                ('package_mapping_url', models.CharField(max_length=256, null=True)),
                ('deeplink_scheme', models.CharField(max_length=128, null=True)),
                ('git_sha_code', models.CharField(max_length=128, null=True)),
                ('git_branch_name', models.CharField(max_length=128, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('snapshot', models.BooleanField()),
                ('library_coordinate_list', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_info.androidproject', to_field='project_name')),
            ],
        ),
        migrations.AddConstraint(
            model_name='iosbuild',
            constraint=models.UniqueConstraint(fields=('project', 'project_version'), name='iosbuild_unique_build'),
        ),
        migrations.AddConstraint(
            model_name='androidbuild',
            constraint=models.UniqueConstraint(fields=('package_name', 'package_version_name', 'product_flavor_name', 'module_name'), name='androidbuild_unique_build'),
        ),
    ]
