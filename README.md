# Financial Analysis Django Project

## Overview

This project is a Django application for analyzing financial transactions from your bank account. The application allows users to upload bank statements in CSV formats, parse and categorize transactions, and visualize expenses through various charts. 

## Features

- **User Authentication**: Secure login and logout functionality.
- **Upload Transactions**: Users can upload bank statements in CSV and PDF formats.
- **Parse Transactions**: Automatic parsing of uploaded files to extract transaction details.
- **Categorize Transactions**: Rules-based categorization of transactions.
- **Budget Comparison**: Compare actual spending against predefined budgets.
- **Visualizations**: Pie charts displaying expenses by category.

## Installation

### Prerequisites

- Python 3.10.11 (https://www.python.org/downloads/)

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/SholaAguns/budgetBuddy.git
    cd budgetBuddy
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```bash
    python manage.py migrate
    ```

5. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

1. **Signup & Login**: This is required to make use of application.

2. **Categories**:
    - The app comes with some predefined categories. The user can remove and add more categories as they like excluding the default "Other" category.
   <img width="952" alt="image" src="https://github.com/SholaAguns/budgetBuddy/assets/106911290/c411bd74-2b62-413e-90cf-62c54c6ea480">

3. **Create Ruleset**:
    - A ruleset is a set of rules that the app will use to categorize your transactions.
   <img width="954" alt="image" src="https://github.com/SholaAguns/budgetBuddy/assets/106911290/1c76bb21-3572-4ef5-acc2-45d549faca6a">

4. **Create Budget**:
    - A budget consists of categories with a set limit. Created budgets can be used for comparison with actual spending.
  <img width="956" alt="image" src="https://github.com/SholaAguns/budgetBuddy/assets/106911290/5d310bc7-f182-4f58-9043-844529958297">

4. **Create Report**:
    - Set name, start & end date and uploade csv sheet of transactions(must have date, name and amount in order as shown in sample_transaction_file.csv)
    - Add an existing ruleset and budget
    - Click on transactions section and click Import transactions
    - Transactions data will be populated
    - Any updates to budget, ruleset or transaction sheet will require transactions are cleared and re-imported.

## Troubleshooting
 1. ImportError: cannot import name 'urlquote' from 'django.utils.http'
    - Open .venv\lib\site-packages\easy_pdf\rendering.py
    - Replace "from django.utils.http import urlquote" with "from urllib.parse import quote as urlquote"
3. ModuleNotFoundError: No module named 'django.utils.six'
   - Open .venv\lib\site-packages\easy_pdf\rendering.py
   - Replace "from django.utils.six import BytesIO" with "from six import BytesIO"
