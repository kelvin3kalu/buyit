# Generated by Django 5.2 on 2025-05-07 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_category_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]
