# Generated by Django 3.2.6 on 2021-08-28 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_book_delivery_factor'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='view_count',
            field=models.BigIntegerField(default=0),
        ),
    ]
