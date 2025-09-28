from random import randint

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
from .models import Category, BudgetCategory, Budget, Rule, Ruleset
from .forms import CategoryForm, BudgetForm, BudgetCategoryForm, RuleForm, RulesetForm, SavingsTrackerForm, \
    SavingsTrackerNameForm, QuickSavingsUpdateForm
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.all().order_by('title')
        return context


class BudgetDetail(LoginRequiredMixin, DetailView):
    model = Budget

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_earnings = self.object.budgetcategory_set.filter(is_earning=True).aggregate(total=Sum('limit'))['total'] or 0
        total_expenses = self.object.budgetcategory_set.filter(is_earning=False).aggregate(total=Sum('limit'))['total'] or 0

        context['total_earnings'] = total_earnings
        context['total_expenses'] = total_expenses
        budget_balance = total_earnings - total_expenses
        context['budget_balance'] = budget_balance
        context['budget_balance_abs'] = abs(budget_balance)

        # Calculate percentages
        total_budget = total_earnings + total_expenses
        if total_budget > 0:
            context['earnings_percentage'] = (total_earnings / total_budget) * 100
            context['expenses_percentage'] = (total_expenses / total_budget) * 100
        else:
            context['earnings_percentage'] = 0
            context['expenses_percentage'] = 0

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
        show_archived = self.request.GET.get('archived', False)
        if show_archived == 'true':
            context['budget_list'] = Budget.objects.filter(user=self.request.user, is_archived=True)
            context['show_archived'] = True
        else:
            context['budget_list'] = Budget.objects.filter(user=self.request.user, is_archived=False)
            context['show_archived'] = False
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

    def form_valid(self, form):
        response = super().form_valid(form)

        # Check if this is a savings category and trigger update
        if hasattr(self.object.category, 'title') and 'Savings' in self.object.category.title:
            savings_service = SavingsService()
            savings_service.trigger_all_users_update()

        return response

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
def quick_update_savings(request, pk):
    savings_tracker = get_object_or_404(SavingsTracker, pk=pk, user=request.user)

    if request.method == 'POST':
        form = QuickSavingsUpdateForm(request.POST, instance=savings_tracker)
        if form.is_valid():
            form.save()

            # Automatically trigger savings calculation update
            savings_service = SavingsService()
            savings_service.update_savings(savings_tracker)

            messages.success(request, f"Current balance updated to ${savings_tracker.current_balance}")
            return redirect('budgets:savings_tracker_detail', pk=savings_tracker.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = QuickSavingsUpdateForm(instance=savings_tracker)

    return render(request, 'budgets/quick_savings_update.html', {
        'form': form,
        'savings_tracker': savings_tracker
    })


@login_required()
def ajax_update_balance(request, pk):
    if request.method == 'POST':
        try:
            savings_tracker = get_object_or_404(SavingsTracker, pk=pk, user=request.user)
            data = json.loads(request.body)
            new_balance = float(data.get('current_balance', 0))

            if new_balance < 0:
                return JsonResponse({'success': False, 'error': 'Balance cannot be negative'})

            # Update balance
            savings_tracker.current_balance = new_balance
            savings_tracker.save()

            # Automatically trigger savings calculation update
            savings_service = SavingsService()
            savings_service.update_savings(savings_tracker)

            return JsonResponse({
                'success': True,
                'new_balance': float(savings_tracker.current_balance)
            })

        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid balance amount'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required()
def toggle_archive_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.is_archived = not budget.is_archived
    budget.save()

    action = "archived" if budget.is_archived else "unarchived"
    messages.success(request, f"Budget {action} successfully")
    return redirect('budgets:single_budget', pk=budget.id)


@login_required()
def bulk_archive_budgets(request):
    if request.method == 'POST':
        selected_budgets = request.POST.getlist('selected_budgets')
        if selected_budgets:
            budgets = Budget.objects.filter(
                id__in=selected_budgets,
                user=request.user,
                is_archived=False
            )
            count = budgets.count()
            budgets.update(is_archived=True)
            messages.success(request, f"{count} budget(s) archived successfully")
        else:
            messages.warning(request, "No budgets selected")

    return redirect('budgets:budget_list')


@login_required()
def bulk_unarchive_budgets(request):
    if request.method == 'POST':
        selected_budgets = request.POST.getlist('selected_budgets')
        if selected_budgets:
            budgets = Budget.objects.filter(
                id__in=selected_budgets,
                user=request.user,
                is_archived=True
            )
            count = budgets.count()
            budgets.update(is_archived=False)
            messages.success(request, f"{count} budget(s) unarchived successfully")
        else:
            messages.warning(request, "No budgets selected")

    return redirect('budgets:budget_list')


@login_required()
def bulk_delete_budgets(request):
    if request.method == 'POST':
        selected_budgets = request.POST.getlist('selected_budgets')
        if selected_budgets:
            budgets = Budget.objects.filter(
                id__in=selected_budgets,
                user=request.user
            )
            count = budgets.count()
            budgets.delete()
            messages.success(request, f"{count} budget(s) deleted successfully")
        else:
            messages.warning(request, "No budgets selected")

    return redirect('budgets:budget_list')


@login_required()
def ajax_update_ruleset_name(request, pk):
    if request.method == 'POST':
        try:
            ruleset = get_object_or_404(Ruleset, pk=pk, user=request.user)
            data = json.loads(request.body)
            new_name = data.get('name', '').strip()

            if not new_name:
                return JsonResponse({'success': False, 'error': 'Name cannot be empty'})

            # Check for uniqueness
            if Ruleset.objects.filter(user=request.user, name=new_name).exclude(pk=pk).exists():
                return JsonResponse({'success': False, 'error': 'A ruleset with this name already exists'})

            ruleset.name = new_name
            ruleset.save()

            return JsonResponse({'success': True, 'new_name': new_name})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required()
def ajax_update_rule(request, pk):
    if request.method == 'POST':
        try:
            rule = get_object_or_404(Rule, pk=pk, ruleset__user=request.user)
            data = json.loads(request.body)
            new_keyword = data.get('keyword', '').strip()
            new_category_id = data.get('category_id')

            if not new_keyword:
                return JsonResponse({'success': False, 'error': 'Keyword cannot be empty'})

            if not new_category_id:
                return JsonResponse({'success': False, 'error': 'Category must be selected'})

            category = get_object_or_404(Category, pk=new_category_id)

            # Check for uniqueness within the ruleset
            if Rule.objects.filter(
                ruleset=rule.ruleset,
                keyword=new_keyword
            ).exclude(pk=pk).exists():
                return JsonResponse({'success': False, 'error': 'A rule with this keyword already exists in this ruleset'})

            rule.keyword = new_keyword
            rule.category = category
            rule.save()

            return JsonResponse({
                'success': True,
                'keyword': new_keyword,
                'category_name': category.title
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required()
def ajax_delete_rule(request, pk):
    if request.method == 'DELETE':
        try:
            rule = get_object_or_404(Rule, pk=pk, ruleset__user=request.user)
            rule.delete()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required()
def ajax_add_rule(request, pk):
    if request.method == 'POST':
        try:
            ruleset = get_object_or_404(Ruleset, pk=pk, user=request.user)
            data = json.loads(request.body)
            keyword = data.get('keyword', '').strip()
            category_id = data.get('category_id')

            if not keyword:
                return JsonResponse({'success': False, 'error': 'Keyword cannot be empty'})

            if not category_id:
                return JsonResponse({'success': False, 'error': 'Category must be selected'})

            category = get_object_or_404(Category, pk=category_id)

            # Check for uniqueness within the ruleset
            if Rule.objects.filter(ruleset=ruleset, keyword=keyword).exists():
                return JsonResponse({'success': False, 'error': 'A rule with this keyword already exists in this ruleset'})

            rule = Rule.objects.create(
                ruleset=ruleset,
                keyword=keyword,
                category=category
            )

            return JsonResponse({
                'success': True,
                'rule_id': rule.id,
                'keyword': keyword,
                'category_name': category.title
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


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
