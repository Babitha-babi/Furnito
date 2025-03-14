# Generated by Django 4.2.17 on 2025-01-03 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0011_product_max_quantity_per_user_product_stock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='zip_code',
            new_name='postal_code',
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.CharField(default='India', max_length=100),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], default='Pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], default='COD', max_length=20)),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
