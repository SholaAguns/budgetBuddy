import csv
from datetime import datetime
from .models import Transaction
from budgets.models import Rule, Category
import fitz  # PyMuPDF


class TransactionService:
    def set_category(rules, transaction_name, is_expense):
        other_expense_category = Category.objects.get(title='Other (Expense)')
        other_earning_category = Category.objects.get(title='Other (Earning)')
        for rule in rules:
            if rule.keyword.lower() in transaction_name.lower():
                return rule.category
        if is_expense:
            return other_expense_category
        else:
            return other_earning_category

    def create_transactions_from_csv(self, report):
        rules = Rule.objects.filter(ruleset=report.ruleset)
        with open(report.transaction_sheet.path, 'r') as f:
            reader = csv.reader(f)
            #next(reader)  # Skip the header row

            for row in reader:
                date_str = row[0].strip()
                name = row[1].strip()
                amount_str = row[2].replace(',', '')  # Remove commas from amount string
                amount = float(amount_str)
                is_expense = amount < 0
                category = TransactionService.set_category(rules, name, is_expense)

                # Parse date from dd/mm/yyyy format to yyyy-mm-dd
                try:
                    date = datetime.strptime(date_str, '%d/%m/%Y').date()
                except ValueError:
                    # Handle invalid date format if necessary
                    date = None



                if report.start_date <= date <= report.end_date:
                    Transaction.objects.create(
                        report=report,
                        name=name,
                        date=date,
                        amount=abs(amount),
                        is_expense=is_expense,
                        category=category
                    )

    def create_transactions_from_pdf(self, report):
        document = fitz.open(report.transaction_sheet.path)
        rules = Rule.objects.filter(ruleset=report.ruleset)
        transactions = []

        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text = page.get_text("text")
            lines = text.split('\n')

            for line in lines:
                # Example logic to parse the transaction data from a line
                try:
                    # Assuming the format is: "DD MMM YY DESCRIPTION LOCATION AMOUNT BALANCE"
                    parts = line.split()
                    if len(parts) < 5:
                        continue

                    date_str = " ".join(parts[0:3])
                    description = " ".join(parts[3:-2])
                    amount_str = parts[-2]
                    date = datetime.strptime(date_str, '%d %b %y').date()

                    # Parse amount, handling for negative amounts
                    amount = float(amount_str.replace(',', '').replace('CR', ''))

                    # Determine if it's an expense or income
                    is_expense = 'CR' not in amount_str

                    # Category could be determined here or later
                    category = TransactionService.set_category(rules, description)

                    if report.start_date <= date <= report.end_date:
                        Transaction.objects.create(
                            report=report,
                            name=description,
                            date=date,
                            amount=abs(amount),
                            is_expense=is_expense,
                            category=category
                        )

                except Exception as e:
                    print(f"Error parsing line: {line} - {e}")




    def clear_transactions(self, report):
        Transaction.objects.filter(report=report).delete()
