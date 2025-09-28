from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps

from .models import BudgetCategory, SavingsTracker
from .services.savings_service import SavingsService


@receiver(post_save, sender=BudgetCategory)
def update_savings_on_budget_category_change(sender, instance, **kwargs):
    """Update all savings trackers when a budget category is modified"""
    savings_service = SavingsService()

    # Check if this is a savings-related category
    if hasattr(instance.category, 'title'):
        if 'Savings' in instance.category.title:
            # Update all savings trackers since this affects projections
            savings_service.trigger_all_users_update()


@receiver(post_delete, sender=BudgetCategory)
def update_savings_on_budget_category_delete(sender, instance, **kwargs):
    """Update all savings trackers when a budget category is deleted"""
    savings_service = SavingsService()

    # Check if this was a savings-related category
    if hasattr(instance.category, 'title'):
        if 'Savings' in instance.category.title:
            # Update all savings trackers since this affects projections
            savings_service.trigger_all_users_update()


def update_savings_on_report_change(sender, instance, **kwargs):
    """Update savings trackers when a report with budget is created/updated"""
    if instance.budget:  # Only if report has a budget
        # Update savings for the report's user
        try:
            savings_tracker = SavingsTracker.objects.get(user=instance.user)
            savings_service = SavingsService()
            savings_service.update_savings(savings_tracker)
        except SavingsTracker.DoesNotExist:
            pass  # No savings tracker for this user


def setup_report_signals():
    """Setup signals for Report model (avoiding circular import)"""
    try:
        Report = apps.get_model('reports', 'Report')
        post_save.connect(update_savings_on_report_change, sender=Report)
        post_delete.connect(update_savings_on_report_change, sender=Report)
    except LookupError:
        pass  # Model not yet loaded