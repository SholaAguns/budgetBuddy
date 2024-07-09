# Custom migration file

from django.db import migrations
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


def populate_rules(apps, schema_editor):
    User = get_user_model()
    Category = apps.get_model('budgets', 'Category')
    Rule = apps.get_model('budgets', 'Rule')
    Ruleset = apps.get_model('budgets', 'Ruleset')
    my_user, created = User.objects.get_or_create(username="Sholzy", email="sholzy@test.com")
    if created:
        my_user.password = make_password("Asecurepassword1")
    my_user.save()

    my_ruleset = Ruleset.objects.create(user=my_user, name='Default Ruleset')

    rules = [
        ["AA MEMBERSHIP", Category.objects.get(title="Car")],
        ["PHAT BUNS", Category.objects.get(title="Takeout")],
        ["Just Eat ", Category.objects.get(title="Takeout")],
        ["TFL TRAVEL", Category.objects.get(title="Transportation and Parking")],
        ["SAINSBURY", Category.objects.get(title="Food and Groceries")],
        ["SIZZLERS", Category.objects.get(title="Takeout")],
        ["RESTAURANT", Category.objects.get(title="Takeout")],
        ["Al Rayan ", Category.objects.get(title="Savings and Investments")],
        ["ETIKA", Category.objects.get(title="Subscriptions")],
        ["LIDL", Category.objects.get(title="Food and Groceries")],
        ["SELECT SUPERMARKET ", Category.objects.get(title="Food and Groceries")],
        ["FIRST RESPONSE", Category.objects.get(title="Car")],
        ["FOOTY ADDICTS", Category.objects.get(title="Sports and Exercise")],
        ["TESCO", Category.objects.get(title="Food and Groceries")],
        ["PARK  BAILEY", Category.objects.get(title="Rent")],
        ["Revolut", Category.objects.get(title="Revolut")],
        ["YOULEND", Category.objects.get(title="Salary")],
        ["AL FATHIHA", Category.objects.get(title="Charity")],
        ["GATWICK AIRPORT", Category.objects.get(title="Transportation and Parking")],
        ["VIRGIN MEDIA", Category.objects.get(title="Utilities")],
        ["Baris", Category.objects.get(title="Food and Groceries")],
        ["PARKING", Category.objects.get(title="Transportation and Parking")],
        ["GoFundMe", Category.objects.get(title="Charity")],
        ["ADMIRAL INSURANCE", Category.objects.get(title="Insurance")],
        ["African Food ", Category.objects.get(title="Food and Groceries")],
        ["CHATGPT", Category.objects.get(title="Subscriptions")],
        ["TRURO", Category.objects.get(title="Takeout")],
        ["MFG WHITGIFT ", Category.objects.get(title="Car")],
        ["CHOPSTIX", Category.objects.get(title="Takeout")],
        ["PRET A MANGER", Category.objects.get(title="Takeout")],
        ["APPLE.COM", Category.objects.get(title="Subscriptions")],
        ["ODEON", Category.objects.get(title="Entertainment")],
        ["UNHCR", Category.objects.get(title="Charity")],
        ["MOSQUE", Category.objects.get(title="Charity")],
        ["Beirut BBQ", Category.objects.get(title="Takeout")],
        ["Grill", Category.objects.get(title="Takeout")],
        ["COFFEE", Category.objects.get(title="Takeout")],
        ["LE BON ", Category.objects.get(title="Takeout")],
        ["CROYDON ISLAMIC", Category.objects.get(title="Charity")],
        ["AFRICA MAR", Category.objects.get(title="Food and Groceries")],
        ["PURE GYM", Category.objects.get(title="Sports and Exercise")],
        ["THAMES WTR", Category.objects.get(title="Utilities")],
        ["WAHED", Category.objects.get(title="Savings and Investments")],
        ["MYTENNIGHT", Category.objects.get(title="Charity")],
        ["PURLEY GR LL", Category.objects.get(title="Takeout")],
    ]

    for keyword, category_title in rules:
        category = Category.objects.get(title=category_title)
        Rule.objects.create(ruleset=my_ruleset, keyword=keyword, category=category)


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0001_initial'),
        ('budgets', '0006_auto_categories'),
    ]

    operations = [
        migrations.RunPython(populate_rules),
    ]
