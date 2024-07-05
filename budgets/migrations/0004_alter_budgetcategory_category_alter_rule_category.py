# Generated by Django 5.0.6 on 2024-07-03 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0003_alter_budget_end_date_alter_budget_start_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetcategory',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='budgets.category'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='budgets.category'),
        ),
    ]
