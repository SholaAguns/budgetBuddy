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
        import sys

        # Get transactions from GoCardless
        date_from_str = date_from or report.start_date.strftime('%Y-%m-%d')

        # If report end date is in the future, use today instead
        today = datetime.now().date()
        if date_to:
            date_to_str = date_to
        elif report.end_date > today:
            date_to_str = today.strftime('%Y-%m-%d')
        else:
            date_to_str = report.end_date.strftime('%Y-%m-%d')

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"IMPORT STARTING", file=sys.stderr)
        print(f"Account ID: {account.account_id}", file=sys.stderr)
        print(f"Date range: {date_from_str} to {date_to_str}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        sys.stderr.flush()

        try:
            print(f"Calling GoCardless API...", file=sys.stderr)
            sys.stderr.flush()
            transactions_data = self.get_account_transactions(
                account.account_id,
                date_from=date_from_str,
                date_to=date_to_str
            )
            print(f"API call completed successfully", file=sys.stderr)
            sys.stderr.flush()
        except Exception as e:
            print(f"EXCEPTION during API call: {type(e).__name__}: {e}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            sys.stderr.flush()
            raise

        # Debug: Print the structure of the response
        print(f"DEBUG: Transaction data type: {type(transactions_data)}", file=sys.stderr)
        print(f"DEBUG: Transaction data keys: {transactions_data.keys() if isinstance(transactions_data, dict) else 'Not a dict'}", file=sys.stderr)
        if isinstance(transactions_data, dict):
            if 'transactions' in transactions_data:
                print(f"DEBUG: transactions key type: {type(transactions_data['transactions'])}", file=sys.stderr)
                print(f"DEBUG: transactions key content preview: {str(transactions_data['transactions'])[:500]}", file=sys.stderr)
        sys.stderr.flush()

        # Get ruleset rules for categorization
        rules = Rule.objects.filter(ruleset=report.ruleset) if report.ruleset else []

        created_count = 0
        skipped_count = 0

        # Handle different possible response structures
        booked_transactions = []

        # Try to extract booked transactions from various possible structures
        if isinstance(transactions_data, dict):
            # Check for nested structure: {'transactions': {'booked': [...], 'pending': [...]}}
            if 'transactions' in transactions_data:
                trans = transactions_data['transactions']
                if isinstance(trans, dict) and 'booked' in trans:
                    booked_transactions = trans['booked']
                elif isinstance(trans, list):
                    # Sometimes transactions might be a direct list
                    booked_transactions = trans
            # Check for flat structure: {'booked': [...], 'pending': [...]}
            elif 'booked' in transactions_data:
                booked_transactions = transactions_data['booked']

        print(f"DEBUG: Found {len(booked_transactions)} booked transactions", file=sys.stderr)
        sys.stderr.flush()

        if not booked_transactions:
            print(f"WARNING: No booked transactions found. Full response structure:", file=sys.stderr)
            import json
            print(json.dumps(transactions_data, indent=2, default=str)[:2000], file=sys.stderr)
            sys.stderr.flush()

        # Process booked transactions
        for txn in booked_transactions:
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
                print(f"Error importing transaction: {e}", file=sys.stderr)
                import traceback
                print(traceback.format_exc(), file=sys.stderr)
                sys.stderr.flush()
                skipped_count += 1
                continue

        # Update last synced timestamp
        account.last_synced = datetime.now()
        account.save()

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"IMPORT COMPLETED: Created={created_count}, Skipped={skipped_count}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        sys.stderr.flush()

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
