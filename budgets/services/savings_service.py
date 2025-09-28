from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

from budgets.models import BudgetCategory, Category
from reports.models import Report
from datetime import date
from budgets.models import ProjectedBalance, SavingsTracker

class SavingsService:
    def update_savings(self, savings_tracker):
        # Get reports with budgets attached, future end dates, ordered by end_date
        reports = Report.objects.filter(
            user=savings_tracker.user,
            budget__isnull=False,
            end_date__gt=date.today()
        ).order_by('end_date')

        # Clear existing projections
        ProjectedBalance.objects.filter(savings_tracker=savings_tracker).delete()

        # Start with current balance
        current_balance = savings_tracker.current_balance

        for report in reports:
            # Get savings categories - default to 0 if not found
            budget_savings_withdrawal = Decimal('0.00')
            budget_savings_deposit = Decimal('0.00')

            try:
                withdrawal_category = Category.objects.get(title="Savings (Withdrawl)")
                withdrawal_budget_cat = BudgetCategory.objects.get(
                    budget=report.budget,
                    category=withdrawal_category
                )
                budget_savings_withdrawal = withdrawal_budget_cat.limit
            except ObjectDoesNotExist:
                pass

            try:
                deposit_category = Category.objects.get(title="Savings (Deposit)")
                deposit_budget_cat = BudgetCategory.objects.get(
                    budget=report.budget,
                    category=deposit_category
                )
                budget_savings_deposit = deposit_budget_cat.limit
            except ObjectDoesNotExist:
                pass

            # Calculate new balance: current + deposits - withdrawals
            new_balance = current_balance + budget_savings_deposit - budget_savings_withdrawal

            # Create projection record
            projected_balance = ProjectedBalance.objects.create(
                savings_tracker=savings_tracker,
                report_id=report.id,
                projected_date=report.end_date,
                balance=new_balance
            )

            # Update current balance for next iteration
            current_balance = new_balance

        # Update final projected values
        if reports.exists():
            final_report = reports.last()
            final_projection = ProjectedBalance.objects.filter(
                savings_tracker=savings_tracker,
                report_id=final_report.id
            ).first()

            if final_projection:
                savings_tracker.final_projected_date = final_projection.projected_date
                savings_tracker.final_projected_balance = final_projection.balance
        else:
            # No future reports, set final values to current
            savings_tracker.final_projected_date = date.today()
            savings_tracker.final_projected_balance = savings_tracker.current_balance

        savings_tracker.save()

    def trigger_all_users_update(self):
        """Update savings for all users - useful when categories are modified"""
        for tracker in SavingsTracker.objects.all():
            self.update_savings(tracker)

    def ensure_savings_categories_exist(self):
        """Ensure required savings categories exist"""
        from budgets.models import Category

        required_categories = [
            "Savings (Deposit)",
            "Savings (Withdrawl)"  # Note: keeping original spelling
        ]

        created_categories = []
        for category_name in required_categories:
            category, created = Category.objects.get_or_create(title=category_name)
            if created:
                created_categories.append(category_name)

        return created_categories



