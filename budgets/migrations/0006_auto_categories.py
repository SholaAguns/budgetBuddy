from django.db import migrations


def populate_categories(apps, schema_editor):
    Category = apps.get_model('budgets', 'Category')
    initial_categories = [
        'Food and Groceries',
        'Utilities',
        'Entertainment',
        'Transportation and Parking',
        'Shopping',
        'Car',
        'Childcare',
        'Insurance',
        'Charity',
        'Salary',
        'Sports and Exercise',
        'Rent',
        'Other (Expense)',
        'Other (Earning)',
        'Takeout',
        'Savings and Investments',
        'Subscriptions',
        'Revolut',
        'Amazon Flex'
    ]
    for category_name in initial_categories:
        Category.objects.create(title=category_name)


class Migration(migrations.Migration):
    dependencies = [
        ('budgets', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_categories),
    ]
