# Generated by Django 3.2 on 2022-03-21 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentosapp', '0007_auto_20220318_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='baipaga',
            name='email',
            field=models.CharField(default='', max_length=80),
        ),
        migrations.AddField(
            model_name='baipaga',
            name='status',
            field=models.CharField(default='CREATED', max_length=60),
        ),
        migrations.AddField(
            model_name='baipaga',
            name='tokenApp',
            field=models.CharField(default='', max_length=1024),
        ),
    ]