# Generated by Django 4.2.17 on 2025-03-11 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0062_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='357a55', max_length=6),
        ),
    ]
