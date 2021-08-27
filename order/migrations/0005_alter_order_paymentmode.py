# Generated by Django 3.2.6 on 2021-08-22 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_paymentmode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paymentMode',
            field=models.CharField(choices=[('C', 'COD'), ('O', 'ONLINE')], max_length=2),
        ),
    ]