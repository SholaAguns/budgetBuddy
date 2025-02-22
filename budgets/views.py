from random import randint

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
from .models import Category, BudgetCategory, Budget, Rule, Ruleset
from .forms import CategoryForm, BudgetForm, BudgetCategoryForm, RuleForm, RulesetForm, SavingsTrackerForm, \
    SavingsTrackerNameForm
from django.urls import reverse
from django.contrib import messages
from budgets.models import SavingsTracker, ProjectedBalance

from .services.savings_service import SavingsService


class CreateCategory(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    redirect_field_name = 'budgets/category_list.html'

class CategoryUpdate(LoginRequiredMixin, UpdateView):
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


from django.http import HttpResponseRedirect
from django.urls import reverse


class CreateSavingsTracker(LoginRequiredMixin, CreateView):
    model = SavingsTracker
    form_class = SavingsTrackerForm
    redirect_field_name = 'budgets/savingstracker_detail.html'

    def form_valid(self, form):
        user = self.request.user
        if SavingsTracker.objects.filter(user=user).exists():
            tracker = SavingsTracker.objects.get(user=user)
            return HttpResponseRedirect(reverse('budgets:savings_tracker_detail', kwargs={'pk': tracker.id}))

        # Create a new SavingsTracker if none exists
        self.object = form.save(commit=False)
        self.object.user = user
        random_number = randint(10000, 99999)
        self.object.name = f'{user} Savings Tracker {random_number}'
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('budgets:savings_tracker_detail', kwargs={'pk': self.object.id})


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_earnings'] = self.object.budgetcategory_set.filter(is_earning=True).aggregate(total=Sum('limit'))['total']
        context['total_expenses'] = self.object.budgetcategory_set.filter(is_earning=False).aggregate(total=Sum('limit'))['total']
        return context

class SavingsTrackerDetail(LoginRequiredMixin, DetailView):
    model = SavingsTracker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projected_balances'] = ProjectedBalance.objects.filter(savings_tracker=self.object)
        return context

class BudgetList(LoginRequiredMixin, ListView):
    model = Budget

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget_list'] = Budget.objects.filter(user=self.request.user)
        return context

class SavingsTrackerList(LoginRequiredMixin, ListView):
    model = SavingsTracker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['savings_tracker_list'] = SavingsTracker.objects.filter(user=self.request.user)
        return context

class CategoryList(LoginRequiredMixin, ListView):
    model = Category


class RulesetList(LoginRequiredMixin, ListView):
    model = Ruleset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruleset_list'] = Ruleset.objects.filter(user=self.request.user)
        return context

class UpdateSavingsTracker(LoginRequiredMixin, UpdateView):
    model = SavingsTracker
    form_class = SavingsTrackerForm
    redirect_field_name = 'budgets/savingstracker_detail.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        savings_service =  SavingsService()
        savings_service.update_savings(self.object)
        self.object.save()
        return super().form_valid(form)

class UpdateSavingsTrackerName(LoginRequiredMixin, UpdateView):
    model = SavingsTracker
    form_class = SavingsTrackerNameForm
    redirect_field_name = 'budgets/savingstracker_detail.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        savings_service =  SavingsService()
        savings_service.update_savings(self.object)
        self.object.save()
        return super().form_valid(form)

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

class BudgetCategoryUpdate(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    model = BudgetCategory
    form_class = BudgetCategoryForm
    redirect_field_name = 'budgets/budget_detail.html'

    def get_success_url(self):
        budgetcategory = BudgetCategory.objects.get(id=self.kwargs['pk'])
        return reverse('budgets:single_budget', kwargs={'pk': budgetcategory.budget.id})

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

class DeleteSavingsTracker(LoginRequiredMixin, DeleteView):
    model = SavingsTracker

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def get_success_url(self):
        return reverse('budgets:savings_tracker_list')

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Savings Tracker Deleted")
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
def update_savings(request, pk):
    savings_tracker = get_object_or_404(SavingsTracker, pk=pk)
    savings_service = SavingsService()
    savings_service.update_savings(savings_tracker)
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
