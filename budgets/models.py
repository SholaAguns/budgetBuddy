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


class Budget(models.Model):
    user = models.ForeignKey(User, related_name='budget', on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=50)
    created_dt = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('budgets:single_budget', kwargs={'pk': self.id})

    class Meta:
        ordering = ['-created_dt']
        unique_together = ['user', 'name']


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, default="")
    limit = models.DecimalField(null=False, max_digits=7, decimal_places=2)

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
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, default="")

    def __str__(self):
        return self.category
