# Example migration file

from django.db import migrations

def populate_categories(apps, schema_editor):
    Category = apps.get_model('yourappname', 'Category')
    initial_categories = [
        'Groceries',
        'Utilities',
        'Entertainment',
        'Transportation',
        'Shopping',
        # Add more initial categories as needed
    ]
    for category_name in initial_categories:
        Category.objects.create(name=category_name)

class Migration(migrations.Migration):

    dependencies = [
        ('yourappname', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_categories),
    ]
