# Generated by Django 3.0.7 on 2020-08-03 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0008_remove_bugs_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='tests',
            name='trace',
            field=models.TextField(blank=True, null=True),
        ),
    ]
