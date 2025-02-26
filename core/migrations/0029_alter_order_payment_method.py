# Generated by Django 4.2.17 on 2025-02-04 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_coupon_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'Cash on Delivery'), ('wallet', 'Wallet'), ('Online', 'Online Payment')], default='COD', max_length=20),
        ),
    ]
