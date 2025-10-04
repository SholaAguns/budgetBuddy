from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, CreateView, ListView
from easy_pdf.views import PDFTemplateView
import json
from django.core.serializers.json import DjangoJSONEncoder
from budgets.models import BudgetCategory
from .models import Report, Transaction, Account
from .forms import AddBudgetForm, AddRulesetForm, ReportForm, ReportNotesForm, TransactionForm
from django.contrib import messages
from .services.transaction_service import TransactionService
from .services.gocardless_service import GoCardlessService


class CreateReport(LoginRequiredMixin, CreateView):
    login_url = '/login'
    model = Report
    form_class = ReportForm
    redirect_field_name = 'reports/report_detail.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class CreateTransaction(LoginRequiredMixin, CreateView):
    login_url = '/login'
    model = Transaction
    form_class = TransactionForm

    def form_valid(self, form):
        report = Report.objects.get(
            id=self.kwargs.get("pk"),
        )

        # Check for duplicate transaction
        duplicate = Transaction.objects.filter(
            report=report,
            name=form.cleaned_data['name'],
            date=form.cleaned_data['date'],
            amount=form.cleaned_data['amount']
        ).first()

        if duplicate:
            messages.warning(self.request, "A transaction with the same date, name, and amount already exists.")
            return HttpResponseRedirect(reverse('reports:single_report', kwargs={'pk': report.id}))

        self.object = form.save(commit=False)
        self.object.report = report
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('reports:single_report', kwargs={'pk': self.object.report.id})


class ReportDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    model = Report

    def get_context_data(self, **kwargs):
        # report = Report.objects.get(
        #     id=self.kwargs.get("pk"),
        # )
        context = super().get_context_data(**kwargs)

        report = self.object
        # budget_categories = report.budget.budgetcategory_set.all()
        budget_categories = BudgetCategory.objects.filter(budget=report.budget)
        budget_category_expenses_total = 0
        total_expenses_by_budget = 0
        budget_category_earnings_total = 0
        total_earnings_by_budget = 0
        total_expense_by_category = {}
        total_earning_by_category = {}

        for budget_category in budget_categories:
            if budget_category.is_earning:
                total_earning_amount = Transaction.objects.filter(report=report, category=budget_category.category, is_expense=False) \
                    .aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')
                total_earning_by_category[budget_category.category.title] = total_earning_amount
                budget_category_earnings_total += budget_category.limit
                total_earnings_by_budget += total_earning_amount

            else:
                total_expense_amount = Transaction.objects.filter(report=report, category=budget_category.category, is_expense=True) \
                    .aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')
                total_expense_by_category[budget_category.category.title] = total_expense_amount
                budget_category_expenses_total += budget_category.limit
                total_expenses_by_budget += total_expense_amount


        expense_differences = {}
        earning_differences = {}
        for cat in budget_categories:
            actual_expenses = total_expense_by_category.get(cat.category.title, Decimal('0.00'))
            expense_differences[cat.category.title] = cat.limit - actual_expenses

            actual_earnings = total_earning_by_category.get(cat.category.title, Decimal('0.00'))
            earning_differences[cat.category.title] = actual_earnings - cat.limit

        context['expense_differences'] = expense_differences
        context['earning_differences'] = earning_differences
        context['total_expenses_difference'] = budget_category_expenses_total - total_expenses_by_budget
        context['total_earnings_difference'] = total_earnings_by_budget - budget_category_earnings_total
        context['total_expense_by_category'] = total_expense_by_category
        context['total_earning_by_category'] = total_earning_by_category
        context['total_expenses_by_budget'] = f'{total_expenses_by_budget:.2f}'
        context['total_earnings_by_budget'] = f'{total_earnings_by_budget:.2f}'
        context['budget_category_expenses_total'] = budget_category_expenses_total
        context['budget_category_earnings_total'] = budget_category_earnings_total

        context['expenses'] = Transaction.objects.filter(report=report, is_expense=True) \
            .annotate(total_amount=Sum('amount')) \
            .order_by('-total_amount')

        expenses_total = Transaction.objects.filter(report=report, is_expense=True) \
                             .aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        context['expenses_total'] = f'{expenses_total:.2f}'

        context['earnings'] = Transaction.objects.filter(report=report, is_expense=False) \
            .annotate(total_amount=Sum('amount')) \
            .order_by('-total_amount')

        earnings_total = Transaction.objects.filter(report=report, is_expense=False) \
                             .aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        context['earnings_total'] = f'{earnings_total:.2f}'

        expenses_by_category = (Transaction.objects.filter(report=report, is_expense=True)
                                .values('category__title')
                                .annotate(total_amount=Sum('amount'))
                                .order_by('-total_amount')[:6])

        earnings_by_category = (Transaction.objects.filter(report=report, is_expense=False)
                                .values('category__title')
                                .annotate(total_amount=Sum('amount'))
                                .order_by('-total_amount')[:6])

        expenses_by_category_json = json.dumps(list(expenses_by_category), cls=DjangoJSONEncoder)
        earnings_by_category_json = json.dumps(list(earnings_by_category), cls=DjangoJSONEncoder)

        context['expenses_by_category'] = expenses_by_category_json
        context['earnings_by_category'] = earnings_by_category_json

        # Get unique categories for filtering
        all_categories = Transaction.objects.filter(report=report).values_list('category__title', flat=True).distinct().order_by('category__title')
        expense_categories = Transaction.objects.filter(report=report, is_expense=True).values_list('category__title', flat=True).distinct().order_by('category__title')
        earning_categories = Transaction.objects.filter(report=report, is_expense=False).values_list('category__title', flat=True).distinct().order_by('category__title')

        context['all_categories'] = list(all_categories)
        context['expense_categories'] = list(expense_categories)
        context['earning_categories'] = list(earning_categories)

        return context


class ReportList(LoginRequiredMixin, ListView):
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_archived = self.request.GET.get('archived', False)
        if show_archived == 'true':
            context['report_list'] = Report.objects.filter(user=self.request.user, is_archived=True)
            context['show_archived'] = True
        else:
            context['report_list'] = Report.objects.filter(user=self.request.user, is_archived=False)
            context['show_archived'] = False
        return context


class ReportUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = Report
    form_class = ReportForm
    redirect_field_name = 'reports/report_detail.html'


class DeleteReport(LoginRequiredMixin, DeleteView):
    model = Report

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def get_success_url(self):
        return reverse('reports:report_list')

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Report Deleted")
        return super().delete(*args, **kwargs)


class TransactionUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = Transaction
    form_class = TransactionForm
    redirect_field_name = 'reports/report_detail.html'

    def get_success_url(self):
        return reverse('reports:single_report', kwargs={'pk': self.object.report.id})



@login_required()
def add_transactions(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if not report.transaction_sheet:
        messages.error(request, "No transaction sheet uploaded for this report.")
        return redirect('reports:single_report', pk=report.id)

    transaction_service = TransactionService()
    if report.transaction_sheet.name.endswith('.pdf'):
        transaction_service.create_transactions_from_pdf(report)
    else:
        transaction_service.create_transactions_from_csv(report)
    report.save()
    return redirect('reports:single_report', pk=report.id)


@login_required()
def add_budget(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = AddBudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.cleaned_data['budget']
            report.budget = budget
            report.save()

            # Update savings tracker if user has one
            try:
                from budgets.models import SavingsTracker
                from budgets.services.savings_service import SavingsService
                savings_tracker = SavingsTracker.objects.get(user=request.user)
                savings_service = SavingsService()
                savings_service.update_savings(savings_tracker)
            except SavingsTracker.DoesNotExist:
                pass  # User doesn't have a savings tracker

        return redirect('reports:single_report', pk=report.id)
    else:
        form = AddBudgetForm(request.user)
        return render(request, 'reports/add_budget_form.html', {'form': form})


@login_required()
def add_ruleset(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = AddRulesetForm(request.user, request.POST)
        if form.is_valid():
            ruleset = form.cleaned_data['ruleset']
            report.ruleset = ruleset
            report.save()
        return redirect('reports:single_report', pk=report.id)
    else:
        form = AddRulesetForm(request.user)
        return render(request, 'reports/add_ruleset_form.html', {'form': form, 'report': report})


@login_required()
def delete_transactions(request, pk):
    report = get_object_or_404(Report, pk=pk)
    transaction_service = TransactionService()
    transaction_service.clear_transactions(report)
    report.save()
    return redirect('reports:single_report', pk=report.id)

@login_required()
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    report =  transaction.report
    transaction.delete()
    return redirect('reports:single_report', pk=report.id)

@login_required()
def analyse_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.analyse_spending()
    return reverse('reports:single_report', kwargs={'pk': report.id})


class ReportPDFView(LoginRequiredMixin, PDFTemplateView):
    template_name = 'reports/report_pdf.html'

    def get_context_data(self, **kwargs):
        report = Report.objects.get(
            id=self.kwargs.get("pk"),
        )
        context = super().get_context_data(**kwargs)
        context['report'] = report
        budget_categories = BudgetCategory.objects.filter(budget=report.budget)
        budget_category_total = 0
        total_expenses_by_budget = 0
        total_by_category = {}

        for budget_category in budget_categories:
            total_amount = Transaction.objects.filter(report=report, category=budget_category.category) \
                               .aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            total_by_category[budget_category.category.title] = f'{total_amount:.2f}'
            budget_category_total += budget_category.limit
            total_expenses_by_budget += total_amount

        context['total_by_category'] = total_by_category
        context['total_expenses_by_budget'] = f'{total_expenses_by_budget:.2f}'
        context['budget_category_total'] = budget_category_total

        context['expenses'] = Transaction.objects.filter(report=report, is_expense=True) \
            .annotate(total_amount=Sum('amount')) \
            .order_by('-total_amount')

        expenses_total = Transaction.objects.filter(report=report, is_expense=True) \
                             .aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        context['expenses_total'] = f'{expenses_total:.2f}'

        context['earnings'] = Transaction.objects.filter(report=report, is_expense=False) \
            .annotate(total_amount=Sum('amount')) \
            .order_by('-total_amount')

        earnings_total = Transaction.objects.filter(report=report, is_expense=False) \
                             .aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        context['earnings_total'] = f'{earnings_total:.2f}'

        expenses_by_category = (Transaction.objects.filter(report=report, is_expense=True)
                                .values('category__title')
                                .annotate(total_amount=Sum('amount'))
                                .order_by('-total_amount')[:6])

        earnings_by_category = (Transaction.objects.filter(report=report, is_expense=False)
                                .values('category__title')
                                .annotate(total_amount=Sum('amount'))
                                .order_by('-total_amount')[:6])

        expenses_by_category_json = json.dumps(list(expenses_by_category), cls=DjangoJSONEncoder)
        earnings_by_category_json = json.dumps(list(earnings_by_category), cls=DjangoJSONEncoder)

        context['expenses_by_category'] = expenses_by_category_json
        context['earnings_by_category'] = earnings_by_category_json

        return context


@login_required()
def update_report_notes(request, pk):
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == 'POST' and is_ajax_request:
        report = get_object_or_404(Report, id=pk)
        form = ReportNotesForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'notes': report.notes})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required()
def toggle_archive_report(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    report.is_archived = not report.is_archived
    report.save()

    action = "archived" if report.is_archived else "unarchived"
    messages.success(request, f"Report {action} successfully")
    return redirect('reports:single_report', pk=report.id)


@login_required()
def bulk_archive_reports(request):
    if request.method == 'POST':
        selected_reports = request.POST.getlist('selected_reports')
        if selected_reports:
            reports = Report.objects.filter(
                id__in=selected_reports,
                user=request.user,
                is_archived=False
            )
            count = reports.count()
            reports.update(is_archived=True)
            messages.success(request, f"{count} report(s) archived successfully")
        else:
            messages.warning(request, "No reports selected")

    return redirect('reports:report_list')


@login_required()
def bulk_unarchive_reports(request):
    if request.method == 'POST':
        selected_reports = request.POST.getlist('selected_reports')
        if selected_reports:
            reports = Report.objects.filter(
                id__in=selected_reports,
                user=request.user,
                is_archived=True
            )
            count = reports.count()
            reports.update(is_archived=False)
            messages.success(request, f"{count} report(s) unarchived successfully")
        else:
            messages.warning(request, "No reports selected")

    return redirect('reports:report_list')


@login_required()
def bulk_delete_reports(request):
    if request.method == 'POST':
        selected_reports = request.POST.getlist('selected_reports')
        if selected_reports:
            reports = Report.objects.filter(
                id__in=selected_reports,
                user=request.user
            )
            count = reports.count()
            reports.delete()
            messages.success(request, f"{count} report(s) deleted successfully")
        else:
            messages.warning(request, "No reports selected")

    return redirect('reports:report_list')


# Bank Account Management Views

class AccountList(LoginRequiredMixin, ListView):
    """List all connected bank accounts"""
    model = Account
    template_name = 'reports/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


@login_required()
def connect_bank_account(request):
    """Initiate bank account connection"""
    if request.method == 'POST':
        institution_id = request.POST.get('institution_id')
        account_name = request.POST.get('account_name', '')

        try:
            service = GoCardlessService()
            redirect_uri = request.build_absolute_uri(reverse('reports:account_callback'))

            requisition_data = service.create_requisition(
                institution_id=institution_id,
                redirect_uri=redirect_uri,
                user_reference=str(request.user.id)
            )

            # Store requisition ID and account name in session
            request.session['requisition_id'] = requisition_data['requisition_id']
            request.session['account_name'] = account_name

            # Redirect to bank authorization
            return redirect(requisition_data['link'])

        except Exception as e:
            import traceback
            print(f"Error in POST connect_bank_account: {traceback.format_exc()}")
            messages.error(request, f"Error connecting account: {str(e)}")
            return redirect('reports:account_list')

    # GET request - show institution selection
    from django.conf import settings

    # Check if credentials are configured
    if not settings.GOCARDLESS_SECRET_ID or not settings.GOCARDLESS_SECRET_KEY:
        messages.error(
            request,
            "GoCardless API credentials not configured. Please add GOCARDLESS_SECRET_ID and "
            "GOCARDLESS_SECRET_KEY to your environment variables. "
            "Get credentials from: https://bankaccountdata.gocardless.com/user-secrets/"
        )
        return redirect('reports:account_list')

    try:
        service = GoCardlessService()
        country_code = request.GET.get('country', 'GB')
        institutions = service.get_institutions(country_code=country_code)

        return render(request, 'reports/connect_account.html', {
            'institutions': institutions,
            'country_code': country_code
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in GET connect_bank_account: {error_details}")
        messages.error(request, f"Error loading banks: {str(e)}. Please check your GoCardless API credentials.")
        return redirect('reports:account_list')


@login_required()
def account_callback(request):
    """Handle callback after bank authorization"""
    requisition_id = request.session.get('requisition_id')
    account_name = request.session.get('account_name', '')

    if not requisition_id:
        messages.error(request, "Invalid callback - no requisition found")
        return redirect('reports:account_list')

    try:
        service = GoCardlessService()
        accounts = service.save_account(request.user, requisition_id, account_name)

        # Clear session data
        del request.session['requisition_id']
        if 'account_name' in request.session:
            del request.session['account_name']

        messages.success(request, f"Successfully connected {len(accounts)} account(s)")
        return redirect('reports:account_list')

    except Exception as e:
        messages.error(request, f"Error saving account: {str(e)}")
        return redirect('reports:account_list')


@login_required()
def disconnect_account(request, pk):
    """Disconnect a bank account"""
    account = get_object_or_404(Account, pk=pk, user=request.user)

    try:
        service = GoCardlessService()
        service.delete_requisition(account.requisition_id)
        account.delete()
        messages.success(request, f"Account '{account.name}' disconnected successfully")
    except Exception as e:
        messages.error(request, f"Error disconnecting account: {str(e)}")

    return redirect('reports:account_list')


@login_required()
def import_from_account(request, pk):
    """Import transactions from a connected account to a report"""
    report = get_object_or_404(Report, pk=pk, user=request.user)

    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        account = get_object_or_404(Account, pk=account_id, user=request.user)

        if not report.ruleset:
            messages.error(request, "Please add a ruleset to the report before importing transactions")
            return redirect('reports:single_report', pk=report.id)

        try:
            service = GoCardlessService()
            created, skipped = service.import_transactions_to_report(
                account=account,
                report=report
            )

            messages.success(
                request,
                f"Imported {created} transaction(s) from {account.name}. Skipped {skipped} duplicate(s)."
            )
        except Exception as e:
            messages.error(request, f"Error importing transactions: {str(e)}")

        return redirect('reports:single_report', pk=report.id)

    # GET request - show account selection
    accounts = Account.objects.filter(user=request.user, is_active=True)
    return render(request, 'reports/import_from_account.html', {
        'report': report,
        'accounts': accounts
    })