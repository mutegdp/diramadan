# Generated by Django 2.2.5 on 2019-10-01 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_views',
            field=models.IntegerField(default=0),
        ),
    ]
