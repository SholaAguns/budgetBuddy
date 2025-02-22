# Generated by Django 5.0.6 on 2024-06-30 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0002_alter_ruleset_options_ruleset_created_dt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='budget',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='budgetcategory',
            name='budget',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgets.budget'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='ruleset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budgets.ruleset'),
        ),
    ]
