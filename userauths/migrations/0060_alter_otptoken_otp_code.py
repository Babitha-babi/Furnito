# Generated by Django 4.2.17 on 2025-03-11 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0059_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='283b71', max_length=6),
        ),
    ]
