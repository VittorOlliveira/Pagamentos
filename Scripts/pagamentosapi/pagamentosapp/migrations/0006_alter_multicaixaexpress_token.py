# Generated by Django 3.2 on 2022-03-18 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentosapp', '0005_multicaixaexpress_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multicaixaexpress',
            name='token',
            field=models.CharField(default='', max_length=1024),
        ),
    ]
