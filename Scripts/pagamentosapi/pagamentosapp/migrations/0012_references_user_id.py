# Generated by Django 3.2 on 2022-07-07 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentosapp', '0011_references'),
    ]

    operations = [
        migrations.AddField(
            model_name='references',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
