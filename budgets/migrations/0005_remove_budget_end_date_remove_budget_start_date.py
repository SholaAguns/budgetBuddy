# Generated by Django 5.0.6 on 2024-07-03 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0004_alter_budgetcategory_category_alter_rule_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='start_date',
        ),
    ]
