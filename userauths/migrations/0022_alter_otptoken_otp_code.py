# Generated by Django 4.2.17 on 2025-01-02 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0021_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='e07835', max_length=6),
        ),
    ]
