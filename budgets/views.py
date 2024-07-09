from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, CreateView, ListView, UpdateView, DeleteView
from .models import Category, BudgetCategory, Budget, Rule, Ruleset
from .forms import CategoryForm, BudgetForm, BudgetCategoryForm, RuleForm, RulesetForm
from django.urls import reverse
from django.contrib import messages


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget_list'] = Budget.objects.filter(user=self.request.user)
        return context


class CategoryList(LoginRequiredMixin, ListView):
    model = Category


class RulesetList(LoginRequiredMixin, ListView):
    model = Ruleset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruleset_list'] = Ruleset.objects.filter(user=self.request.user)
        return context


class BudgetUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = Budget
    form_class = BudgetForm
    redirect_field_name = 'budgets/budget_detail.html'


class RulesetUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = Ruleset
    form_class = RulesetForm
    redirect_field_name = 'budgets/ruleset_detail.html'


class DeleteBudget(LoginRequiredMixin, DeleteView):
    model = Budget

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def get_success_url(self):
        return reverse('budgets:budget_list')

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Budget Deleted")
        return super().delete(*args, **kwargs)


class DeleteRuleset(LoginRequiredMixin, DeleteView):
    model = Ruleset

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def get_success_url(self):
        return reverse('budgets:rulesets')

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Ruleset Deleted")
        return super().delete(*args, **kwargs)


@login_required()
def category_remove(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def rule_remove(request, pk):
    rule = get_object_or_404(Rule, pk=pk)
    rule.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def budgetcategory_remove(request, pk):
    budgetcategory = get_object_or_404(BudgetCategory, pk=pk)
    budgetcategory.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def budget_duplicate(request, pk):
    existing_budget = get_object_or_404(Budget, pk=pk)
    existing_budget_categories = BudgetCategory.objects.filter(budget=existing_budget)
    new_budget = existing_budget
    new_budget.pk = None
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            new_budget.name = name
            new_budget.save()
            for category in existing_budget_categories:
                new_category = category
                new_category.pk = None
                new_category.budget = new_budget
                new_category.save()
        return redirect('budgets:single_budget', pk=new_budget.id)
    else:
        form = BudgetForm(request.POST)
        return render(request, 'budgets/budget_form.html', {'form': form, 'budget': existing_budget})


@login_required()
def ruleset_duplicate(request, pk):
    existing_ruleset = get_object_or_404(Ruleset, pk=pk)
    existing_rules = Rule.objects.filter(ruleset=existing_ruleset)
    new_ruleset = existing_ruleset
    new_ruleset.pk = None
    if request.method == 'POST':
        form = RulesetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            new_ruleset.name = name
            new_ruleset.save()
            for rule in existing_rules:
                new_rule = rule
                new_rule.pk = None
                new_rule.ruleset = new_ruleset
                new_rule.save()
        return redirect('budgets:single_ruleset', pk=new_ruleset.id)
    else:
        form = RulesetForm(request.POST)
        return render(request, 'budgets/ruleset_form.html', {'form': form, 'ruleset': existing_ruleset})