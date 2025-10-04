from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.contrib.auth import get_user_model
from budgets.models import Budget, Ruleset, Category
from django.core.validators import FileExtensionValidator

User = get_user_model()


class Report(models.Model):
    name = models.CharField(default="", max_length=50, unique=True)
    transaction_sheet = models.FileField(upload_to='sheets', blank=True, null=True,
                                         validators=[FileExtensionValidator(['csv',]
                                                                            )])
    user = models.ForeignKey(User, related_name='report', on_delete=models.CASCADE)
    created_dt = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.ForeignKey(Budget, on_delete=models.DO_NOTHING, null=True)
    ruleset = models.ForeignKey(Ruleset, on_delete=models.DO_NOTHING, null=True)
    notes = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_dt']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('reports:single_report', kwargs={'pk': self.id})

    def addruleset(self, ruleset):
        self.ruleset = ruleset
        self.save()

    def addbudget(self, budget):
        self.budget = budget
        self.save()

    def analyse_spending(self):
        pass

    def total_by_category(self, category):
        transactions = self.transaction_set.filter(category=category)
        total_spending = transactions.aggregate(total=Sum('amount'))['total'] or 0
        return total_spending


class Account(models.Model):
    """Represents a connected bank account via GoCardless"""
    user = models.ForeignKey(User, related_name='bank_accounts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Custom name for this account")
    institution_name = models.CharField(max_length=200, blank=True, null=True)

    # GoCardless specific fields
    requisition_id = models.CharField(max_length=100, unique=True, help_text="GoCardless requisition ID")
    account_id = models.CharField(max_length=100, unique=True, help_text="GoCardless account ID")
    iban = models.CharField(max_length=34, blank=True, null=True)

    # Status and metadata
    is_active = models.BooleanField(default=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-connected_at']
        unique_together = ['user', 'account_id']

    def __str__(self):
        return f"{self.name} ({self.institution_name or 'Bank Account'})"


class Transaction(models.Model):
    name = models.CharField(default="", max_length=150)
    date = models.DateField()
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    is_expense = models.BooleanField(default=False)

    # Optional link to bank account
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name='transactions')
    external_id = models.CharField(max_length=200, blank=True, null=True, help_text="External transaction ID from bank")

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ['-date']