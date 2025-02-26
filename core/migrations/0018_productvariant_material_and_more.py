# Generated by Django 4.2.17 on 2025-01-08 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_productvariant'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='material',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='variant_images',
            field=models.ManyToManyField(blank=True, related_name='variant_images', to='core.productimages'),
        ),
    ]
