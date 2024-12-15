from decimal import Decimal

from django.contrib.auth.decorators import login_required
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
from .models import Report, Transaction
from .forms import AddBudgetForm, AddRulesetForm, ReportForm, ReportNotesForm, TransactionForm
from django.contrib import messages
from .services import TransactionService


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
        self.object = form.save(commit=False)
        report = Report.objects.get(
            id=self.kwargs.get("pk"),
        )
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
        budget_category_total = 0
        total_expenses_by_budget = 0
        total_by_category = {}

        for budget_category in budget_categories:
            total_amount = Transaction.objects.filter(report=report, category=budget_category.category, is_earning=False) \
                               .aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.00')
            total_by_category[budget_category.category.title] = total_amount
            budget_category_total += budget_category.limit
            total_expenses_by_budget += total_amount

        differences = {}
        for cat in budget_categories:
            actual = total_by_category.get(cat.category.title, Decimal('0.00'))
            differences[cat.category.title] = cat.limit - actual

        context['differences'] = differences
        context['total_difference'] = budget_category_total - total_expenses_by_budget
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


class ReportList(LoginRequiredMixin, ListView):
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_list'] = Report.objects.filter(user=self.request.user)
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


@login_required()
def add_transactions(request, pk):
    report = get_object_or_404(Report, pk=pk)
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