# Generated by Django 3.2.6 on 2021-08-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20210824_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='_password',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
