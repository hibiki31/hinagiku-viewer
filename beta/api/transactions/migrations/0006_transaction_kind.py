# Generated by Django 3.2.6 on 2021-09-11 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_auto_20210901_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='kind',
            field=models.CharField(default='expenses', max_length=8),
        ),
    ]
