# Generated by Django 3.2 on 2022-03-14 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentosapp', '0003_multicaixaexpress'),
    ]

    operations = [
        migrations.AddField(
            model_name='multicaixaexpress',
            name='status',
            field=models.CharField(default='CREATED', max_length=60),
        ),
    ]
