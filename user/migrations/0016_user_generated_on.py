# Generated by Django 3.2.6 on 2021-08-29 09:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_auto_20210829_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='generated_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
