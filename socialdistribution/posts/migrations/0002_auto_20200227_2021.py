# Generated by Django 3.0.3 on 2020-02-27 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='published',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date published'),
        ),
    ]
