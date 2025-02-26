# Generated by Django 4.2.17 on 2024-12-21 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0016_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='3b02bd', max_length=6),
        ),
    ]
