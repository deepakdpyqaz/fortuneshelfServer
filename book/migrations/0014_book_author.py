# Generated by Django 3.2.6 on 2021-09-09 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0013_remove_book_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.CharField(default='A.C. Bhaktivedanta Swami Srila Prabhupada', max_length=100),
        ),
    ]
