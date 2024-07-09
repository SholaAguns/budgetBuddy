# Generated by Django 5.0.6 on 2024-07-07 11:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_report_transaction_sheet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='transaction_sheet',
            field=models.FileField(upload_to='sheets', validators=[django.core.validators.FileExtensionValidator(['csv'])]),
        ),
    ]