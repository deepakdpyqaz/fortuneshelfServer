# Generated by Django 3.2.6 on 2021-08-24 12:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userunverified',
            name='address',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='city',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='country',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='district',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='otpGenTime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='pincode',
            field=models.CharField(default='', max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userunverified',
            name='state',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
