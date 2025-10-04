from datetime import datetime, timedelta
from django.conf import settings
from nordigen import NordigenClient
from reports.models import Account, Transaction
from budgets.models import Rule


class GoCardlessService:
    """Service to handle GoCardless Bank Account Data API integration"""

    def __init__(self):
        # Initialize the Nordigen client (GoCardless Bank Account Data API)
        self.client = NordigenClient(
            secret_id=getattr(settings, 'GOCARDLESS_SECRET_ID', ''),
            secret_key=getattr(settings, 'GOCARDLESS_SECRET_KEY', '')
        )
        self._ensure_token()

    def _ensure_token(self):
        """Generate a new access token"""
        token_data = self.client.generate_token()
        # Token is automatically stored in the client

    def get_institutions(self, country_code='GB'):
        """Get list of available banks for a country"""
        return self.client.institution.get_institutions(country=country_code)

    def create_requisition(self, institution_id, redirect_uri, user_reference=None):
        """
        Create a requisition (authorization link) for bank connection

        Args:
            institution_id: The bank institution ID
            redirect_uri: URL to redirect user after authorization
            user_reference: Optional reference to identify the user

        Returns:
            dict with 'link' (authorization URL) and 'requisition_id'
        """
        requisition = self.client.initialize_session(
            institution_id=institution_id,
            redirect_uri=redirect_uri,
            reference_id=user_reference
        )
        return {
            'link': requisition.link,
            'requisition_id': requisition.requisition_id
        }

    def get_requisition_status(self, requisition_id):
        """Check if requisition is completed and get account IDs"""
        requisition = self.client.requisition.get_requisition_by_id(
            requisition_id=requisition_id
        )
        return requisition

    def get_account_details(self, account_id):
        """Get account metadata (IBAN, name, etc.)"""
        account = self.client.account_api(id=account_id)
        metadata = account.get_metadata()
        details = account.get_details()
        return {
            'metadata': metadata,
            'details': details
        }

    def get_account_balances(self, account_id):
        """Get account balances"""
        account = self.client.account_api(id=account_id)
        return account.get_balances()

    def get_account_transactions(self, account_id, date_from=None, date_to=None):
        """
        Get transactions for an account

        Args:
            account_id: GoCardless account ID
            date_from: Start date (defaults to 90 days ago)
            date_to: End date (defaults to today)

        Returns:
            List of transactions
        """
        account = self.client.account_api(id=account_id)

        # Default to last 90 days if not specified
        if not date_from:
            date_from = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')

        transactions = account.get_transactions(date_from=date_from, date_to=date_to)
        return transactions

    def save_account(self, user, requisition_id, account_name=None):
        """
        Save connected account to database

        Args:
            user: Django user object
            requisition_id: GoCardless requisition ID
            account_name: Optional custom name for the account

        Returns:
            Created Account instance(s)
        """
        requisition = self.get_requisition_status(requisition_id)

        if requisition['status'] != 'LN':  # LN = Linked
            raise ValueError(f"Requisition not completed. Status: {requisition['status']}")

        accounts = []
        for account_id in requisition['accounts']:
            # Get account details
            details = self.get_account_details(account_id)

            # Extract IBAN if available
            iban = None
            if 'details' in details and 'iban' in details['details']:
                iban = details['details']['iban']

            # Get institution name
            institution_name = requisition.get('institution_id', 'Unknown Bank')

            # Create or update account
            account, created = Account.objects.update_or_create(
                account_id=account_id,
                defaults={
                    'user': user,
                    'name': account_name or f"Account {account_id[:8]}",
                    'institution_name': institution_name,
                    'requisition_id': requisition_id,
                    'iban': iban,
                    'is_active': True
                }
            )
            accounts.append(account)

        return accounts

    def import_transactions_to_report(self, account, report, date_from=None, date_to=None):
        """
        Import transactions from a connected account to a report

        Args:
            account: Account model instance
            report: Report model instance
            date_from: Start date for transactions
            date_to: End date for transactions

        Returns:
            Tuple of (created_count, skipped_count)
        """
        # Get transactions from GoCardless
        transactions_data = self.get_account_transactions(
            account.account_id,
            date_from=date_from or report.start_date.strftime('%Y-%m-%d'),
            date_to=date_to or report.end_date.strftime('%Y-%m-%d')
        )

        # Get ruleset rules for categorization
        rules = Rule.objects.filter(ruleset=report.ruleset) if report.ruleset else []

        created_count = 0
        skipped_count = 0

        # Process booked transactions
        for txn in transactions_data.get('transactions', {}).get('booked', []):
            try:
                # Parse transaction data
                transaction_id = txn.get('transactionId') or txn.get('internalTransactionId')

                # Parse date
                date_str = txn.get('bookingDate') or txn.get('valueDate')
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Skip if outside report date range
                if not (report.start_date <= transaction_date <= report.end_date):
                    skipped_count += 1
                    continue

                # Get transaction amount
                amount = float(txn['transactionAmount']['amount'])
                is_expense = amount < 0

                # Get description/name
                name = txn.get('remittanceInformationUnstructured',
                              txn.get('additionalInformation', 'Bank Transaction'))

                # Determine category
                category = self._categorize_transaction(rules, name, is_expense)

                # Create transaction (using get_or_create to avoid duplicates)
                transaction, created = Transaction.objects.get_or_create(
                    report=report,
                    name=name[:150],  # Truncate to model max_length
                    date=transaction_date,
                    amount=abs(amount),
                    defaults={
                        'is_expense': is_expense,
                        'category': category,
                        'account': account,
                        'external_id': transaction_id
                    }
                )

                if created:
                    created_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                print(f"Error importing transaction: {e}")
                skipped_count += 1
                continue

        # Update last synced timestamp
        account.last_synced = datetime.now()
        account.save()

        return created_count, skipped_count

    def _categorize_transaction(self, rules, transaction_name, is_expense):
        """Categorize a transaction based on rules"""
        from budgets.models import Category

        other_expense_category = Category.objects.get(title='Other (Expense)')
        other_earning_category = Category.objects.get(title='Other (Earning)')

        for rule in rules:
            if rule.keyword.lower() in transaction_name.lower():
                return rule.category

        if is_expense:
            return other_expense_category
        else:
            return other_earning_category

    def delete_requisition(self, requisition_id):
        """Delete a requisition (disconnects account)"""
        self.client.requisition.delete_requisition(requisition_id=requisition_id)
