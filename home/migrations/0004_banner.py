# Generated by Django 3.2.6 on 2021-09-30 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_pincode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='banner')),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
