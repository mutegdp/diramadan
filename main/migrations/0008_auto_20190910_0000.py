# Generated by Django 2.2.5 on 2019-09-09 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_product_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, to='main.ProductTag'),
        ),
    ]
