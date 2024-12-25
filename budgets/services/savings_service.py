from django.core.exceptions import ObjectDoesNotExist

from budgets.models import BudgetCategory, Category
from reports.models import Report
from datetime import date
from budgets.models import ProjectedBalance, SavingsTracker

class SavingsService:
    def update_savings(self, savings_tracker):
        reports = Report.objects.filter(user=savings_tracker.user).order_by('end_date')
        ProjectedBalance.objects.filter(savings_tracker=savings_tracker).delete()

        savings_balance = savings_tracker.current_balance

        for report in reports:
            if report.end_date > date.today():
                try:
                    withdrawl_category = Category.objects.get(title="Savings (Withdrawl)")
                    deposit_category = Category.objects.get(title="Savings (Deposit)")
                    budget_savings_withdrawl = (BudgetCategory.objects
                                                .get(budget=report.budget, category=withdrawl_category).limit)
                    budget_savings_deposit = (BudgetCategory.objects
                                              .get(budget=report.budget, category=deposit_category).limit)
                except ObjectDoesNotExist:
                    budget_savings_withdrawl = None
                    budget_savings_deposit = None



                projected_balance, created = ProjectedBalance.objects.get_or_create(
                    savings_tracker=savings_tracker,
                    report_id=report.id,
                    projected_date=report.end_date,
                    balance=savings_balance + budget_savings_deposit - budget_savings_withdrawl
                )
                savings_balance = projected_balance.balance
                projected_balance.report_id = report.id
                projected_balance.save()
                savings_tracker.final_projected_date = projected_balance.projected_date
                savings_tracker.final_projected_balance = projected_balance.balance
                savings_tracker.save()



