# Generated by Django 3.1 on 2020-08-16 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0009_tests_trace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testjobs',
            name='custom_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
