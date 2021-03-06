# Generated by Django 3.2.6 on 2021-09-17 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_coupon_generated_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='courier_name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='courier_tracking_id',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='courier_url',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
