# Generated by Django 4.2.17 on 2024-12-21 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0012_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='c51049', max_length=6),
        ),
    ]
