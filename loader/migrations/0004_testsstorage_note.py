# Generated by Django 2.2.8 on 2020-01-06 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0003_testsstorage_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='testsstorage',
            name='note',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
