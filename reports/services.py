import csv
from datetime import datetime
from .models import Transaction
from budgets.models import Rule, Category


class TransactionService:
    def set_category(rules, transaction_name):
        other_category = Category.objects.get(title='Other')
        for rule in rules:
            if rule.keyword.lower in transaction_name():
                return rule.category

        return other_category

    def create_transactions(self, report):
        rules = Rule.objects.filter(ruleset=report.ruleset)
        with open(report.transaction_sheet.path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row

            for row in reader:
                date_str = row[0].strip()
                name = row[1].strip()
                amount_str = row[2].replace(',', '')  # Remove commas from amount string
                amount = float(amount_str)
                category = TransactionService.set_category(rules, name)

                # Parse date from dd/mm/yyyy format to yyyy-mm-dd
                try:
                    date = datetime.strptime(date_str, '%d/%m/%Y').date().isoformat()
                except ValueError:
                    # Handle invalid date format if necessary
                    date = None

                is_expense = amount < 0

                Transaction.objects.create(
                    report=report,
                    name=name,
                    date=date,
                    amount=abs(amount),
                    is_expense=is_expense,
                    category=category
                )
