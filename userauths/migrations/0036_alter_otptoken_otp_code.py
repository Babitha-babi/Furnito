# Generated by Django 4.2.17 on 2025-01-08 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0035_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='ffedc5', max_length=6),
        ),
    ]
