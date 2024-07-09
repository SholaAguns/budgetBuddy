# Example migration file

from django.db import migrations


def populate_categories(apps, schema_editor):
    Category = apps.get_model('budgets', 'Category')
    initial_categories = [
        'Food and Groceries',
        'Utilities',
        'Entertainment',
        'Transportation',
        'Shopping',
        'Car',
        'Insurance',
        'Charity',
        'Salary',
        'Sports and Exercise',
        'Rent',
        'Other',
        'Takeout'


        # Add more initial categories as needed
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
