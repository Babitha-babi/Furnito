# Generated by Django 4.2.17 on 2024-12-20 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0006_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='23dc38', max_length=6),
        ),
    ]
