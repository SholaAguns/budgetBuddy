from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    title = models.CharField(default="", max_length=50, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('budgets:categories')

    class Meta:
        ordering = ['title']


class Budget(models.Model):
    user = models.ForeignKey(User, related_name='budget', on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=50)
    created_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('budgets:single_budget', kwargs={'pk': self.id})

    class Meta:
        ordering = ['-created_dt']
        unique_together = ['user', 'name']


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default="")
    limit = models.DecimalField(null=False, max_digits=7, decimal_places=2)
    is_earning = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.category


class Ruleset(models.Model):
    user = models.ForeignKey(User, related_name='ruleset', on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=50)
    created_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('budgets:single_ruleset', kwargs={'pk': self.id})

    class Meta:
        ordering = ['-created_dt']
        unique_together = ['user', 'name']


class Rule(models.Model):
    ruleset = models.ForeignKey(Ruleset, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.category

    class Meta:
        unique_together = ['keyword', 'ruleset']

class SavingsTracker(models.Model):
    current_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=7)
    final_projected_balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=7)
    final_projected_date = models.DateField(null=True)
    user = models.OneToOneField(User, related_name='savingstracker', on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=50)
    created_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.current_balance

class ProjectedBalance(models.Model):
    balance = models.DecimalField(default=0.00, decimal_places=2, max_digits=7)
    projected_date = models.DateField(null=True)
    report_id = models.IntegerField()
    savings_tracker = models.ForeignKey(SavingsTracker, related_name='projectedbalance', on_delete=models.CASCADE)