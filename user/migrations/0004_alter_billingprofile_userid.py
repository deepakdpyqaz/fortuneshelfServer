# Generated by Django 3.2.6 on 2021-08-21 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20210821_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingprofile',
            name='userId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_profile', to='user.user'),
        ),
    ]
