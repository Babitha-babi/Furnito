# Generated by Django 4.2.17 on 2025-01-02 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0024_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='bcdf8f', max_length=6),
        ),
    ]
