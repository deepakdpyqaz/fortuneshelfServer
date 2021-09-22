# Generated by Django 3.2.6 on 2021-09-17 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_auto_20210917_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='dimension',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='weight',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]