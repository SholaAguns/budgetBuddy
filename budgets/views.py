from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, CreateView, ListView
from .models import Category, BudgetCategory, Budget, Rule, Ruleset
from .forms import CategoryForm, BudgetForm, BudgetCategoryForm, RuleForm, RulesetForm
from django.urls import reverse


class CreateCategory(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    redirect_field_name = 'budgets/category_list.html'


class CreateBudget(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    redirect_field_name = 'budgets/budget_detail.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class CreateRuleset(LoginRequiredMixin, CreateView):
    model = Ruleset
    form_class = RulesetForm
    redirect_field_name = 'budgets/ruleset_list.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class CreateBudgetCategory(LoginRequiredMixin, CreateView):
    model = BudgetCategory
    form_class = BudgetCategoryForm
    template_name = 'budgets/budgetcategory_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.budget = Budget.objects.get(id=self.kwargs['pk'])
        self.object.save()
        form.save()
        return super().form_valid(form)


    def get_success_url(self):
        budget = Budget.objects.get(id=self.kwargs['pk'])
        return reverse('budgets:single_budget', kwargs={'pk': budget.id})


class CreateRule(LoginRequiredMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = 'budgets/rule_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.ruleset = Ruleset.objects.get(id=self.kwargs['pk'])
        self.object.save()
        form.save()
        return super().form_valid(form)


    def get_success_url(self):
        ruleset = Ruleset.objects.get(id=self.kwargs['pk'])
        return reverse('budgets:single_ruleset', kwargs={'pk': ruleset.id})


class RulesetDetail(LoginRequiredMixin, DetailView):
    model = Ruleset


class BudgetDetail(LoginRequiredMixin, DetailView):
    model = Budget


class BudgetList(LoginRequiredMixin, ListView):
    model = Budget


class CategoryList(LoginRequiredMixin, ListView):
    model = Category


class RulesetList(LoginRequiredMixin, ListView):
    model = Ruleset
