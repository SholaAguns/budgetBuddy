from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, CreateView, ListView
from .models import Report, Transaction
from .forms import AddBudgetForm, AddRulesetForm, ReportForm
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


class ReportDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    model = Report


class ReportList(LoginRequiredMixin, ListView):
    model = Report
    login_url = '/login'


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
    transaction_service.create_transactions(report)
    report.save()
    return redirect('reports:single_report', pk=report.id)


@login_required()
def add_budget(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = AddBudgetForm(request.POST)
        if form.is_valid():
            budget = form.cleaned_data['budget']
            report.budget = budget
            report.save()
        return redirect('reports:single_report', pk=report.id)
    else:
        form = AddBudgetForm()
        return render(request, 'reports/add_budget_form.html', {'form': form})


@login_required()
def add_ruleset(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = AddRulesetForm(request.POST)
        if form.is_valid():
            ruleset = form.cleaned_data['ruleset']
            report.ruleset = ruleset
            report.save()
        return redirect('reports:single_report', pk=report.id)
    else:
        form = AddRulesetForm()
        return render(request, 'reports/add_ruleset_form.html', {'form': form, 'report': report})


@login_required()
def analyse_spending(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.analyse_spending()
    return reverse('reports:single_report', kwargs={'pk': report.id})