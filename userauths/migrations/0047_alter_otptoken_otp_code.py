# Generated by Django 4.2.17 on 2025-01-20 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0046_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='f6f831', max_length=6),
        ),
    ]
