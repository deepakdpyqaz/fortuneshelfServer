# Generated by Django 3.2.6 on 2021-08-21 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='created_on',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
