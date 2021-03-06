# Generated by Django 3.2.6 on 2021-09-10 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_auto_20210828_0944'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.CharField(max_length=50)),
                ('discount', models.FloatField(default=0.0)),
                ('isValid', models.BooleanField(default=True)),
                ('usage', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.coupon'),
        ),
    ]
