# Generated by Django 4.2.17 on 2025-02-03 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0054_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='9aa9b5', max_length=6),
        ),
    ]
