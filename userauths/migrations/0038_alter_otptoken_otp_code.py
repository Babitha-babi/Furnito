# Generated by Django 4.2.17 on 2025-01-11 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0037_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='ed7e06', max_length=6),
        ),
    ]
