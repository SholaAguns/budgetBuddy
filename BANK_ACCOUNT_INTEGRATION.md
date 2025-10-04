# Bank Account Integration with GoCardless

This feature allows you to connect real bank accounts via the GoCardless Bank Account Data API and automatically import transactions into your reports.

## Setup Instructions

### 1. Get GoCardless API Credentials

1. Sign up for a GoCardless Bank Account Data account at: https://bankaccountdata.gocardless.com/
2. Navigate to User Secrets: https://bankaccountdata.gocardless.com/user-secrets/
3. Copy your `Secret ID` and `Secret Key`

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your GoCardless credentials to `.env`:
   ```
   GOCARDLESS_SECRET_ID=your-secret-id-here
   GOCARDLESS_SECRET_KEY=your-secret-key-here
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

## How to Use

### Connecting a Bank Account

1. Navigate to **Bank Accounts** in the main menu
2. Click **Connect New Account**
3. Select your country and bank
4. Enter an optional custom name for the account
5. Click **Connect Account** - you'll be redirected to your bank's login page
6. Authorize the connection
7. You'll be redirected back to BudgetBuddy with your account connected

### Importing Transactions

1. Open a report
2. Ensure the report has a **ruleset** attached (required for categorization)
3. Click **Import from Bank Account** in the transactions section
4. Select the connected bank account
5. Click **Import Transactions**
6. Transactions within the report's date range will be imported and automatically categorized

### Features

- **Automatic Categorization**: Transactions are categorized using your ruleset rules
- **Duplicate Prevention**: The system automatically skips duplicate transactions based on date, name, and amount
- **Date Filtering**: Only transactions within the report date range are imported
- **Multi-Account Support**: Connect multiple bank accounts
- **Transaction Tracking**: Each transaction stores its external bank ID for reference

### Managing Connected Accounts

- **View Accounts**: See all connected accounts, connection dates, and last sync times
- **Disconnect**: Remove account connections when no longer needed
- Accounts are linked to your user account and private

## Technical Details

### Models

**Account Model** (`reports/models.py`):
- Stores bank account connection details
- Fields: name, institution_name, requisition_id, account_id, IBAN
- Tracks connection and sync status

**Transaction Model Updates**:
- New fields: `account` (ForeignKey) and `external_id`
- Links transactions to their source bank account

### Services

**GoCardlessService** (`reports/services/gocardless_service.py`):
- Handles all API interactions with GoCardless
- Methods:
  - `create_requisition()`: Initiate bank connection
  - `get_account_transactions()`: Fetch transactions
  - `import_transactions_to_report()`: Import with categorization
  - `save_account()`: Store connected account details

### Views

- `AccountList`: View all connected accounts
- `connect_bank_account()`: Initiate connection flow
- `account_callback()`: Handle post-authorization callback
- `disconnect_account()`: Remove account connection
- `import_from_account()`: Import transactions to report

### URL Routes

- `/reports/accounts/` - List connected accounts
- `/reports/accounts/connect/` - Connect new account
- `/reports/accounts/callback/` - OAuth callback
- `/reports/accounts/<id>/disconnect/` - Disconnect account
- `/reports/report/<id>/import_from_account/` - Import transactions

## Supported Countries & Banks

GoCardless supports over 2,000 banks across Europe, including:
- 🇬🇧 United Kingdom
- 🇮🇪 Ireland
- 🇩🇪 Germany
- 🇫🇷 France
- 🇪🇸 Spain
- 🇮🇹 Italy
- 🇳🇱 Netherlands
- And many more...

## Security & Privacy

- All bank connections use OAuth 2.0 secure authorization
- API credentials are stored as environment variables
- Bank passwords are never stored in the application
- Each user can only access their own connected accounts
- Supports account disconnection at any time

## Troubleshooting

### "No module named 'nordigen'" Error
Run: `pip install nordigen`

### "Invalid callback" Error
Ensure your requisition completed successfully. Try reconnecting the account.

### Transactions Not Importing
1. Verify the report has a ruleset attached
2. Check that transactions fall within the report date range
3. Ensure the account connection is still active

### API Credentials Not Working
1. Verify credentials in `.env` file
2. Check credentials are correct at https://bankaccountdata.gocardless.com/user-secrets/
3. Ensure environment variables are loaded (restart Django server)

## API Documentation

For more details on the GoCardless Bank Account Data API:
- Quick Start: https://developer.gocardless.com/bank-account-data/quick-start-guide
- API Reference: https://developer.gocardless.com/bank-account-data/overview
