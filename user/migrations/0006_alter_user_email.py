# Generated by Django 3.2.6 on 2021-08-21 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_userunverified_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]