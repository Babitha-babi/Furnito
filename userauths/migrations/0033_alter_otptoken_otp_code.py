# Generated by Django 4.2.17 on 2025-01-05 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0032_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='7a5355', max_length=6),
        ),
    ]
