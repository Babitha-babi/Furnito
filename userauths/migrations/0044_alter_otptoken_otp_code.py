# Generated by Django 4.2.17 on 2025-01-15 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0043_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='f06bba', max_length=6),
        ),
    ]
