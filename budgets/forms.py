from django import forms
from .models import Category, Budget, BudgetCategory, Ruleset, Rule
from budgets.models import SavingsTracker


class DateInput(forms.DateInput):
    input_type = 'date'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('title', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # Check if the instance exists (update mode)
            self.fields['title'].widget.attrs['placeholder'] = self.instance.title



class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ('name',)



class BudgetCategoryForm(forms.ModelForm):

    class Meta:
        model = BudgetCategory
        fields = ('category', 'limit', 'is_earning',)


class RulesetForm(forms.ModelForm):

    class Meta:
        model = Ruleset
        fields = ('name',)


class RuleForm(forms.ModelForm):

    class Meta:
        model = Rule
        fields = ('keyword', 'category',)

class SavingsTrackerForm(forms.ModelForm):

    class Meta:
        model = SavingsTracker
        fields = ('current_balance',)

class SavingsTrackerNameForm(forms.ModelForm):

    class Meta:
        model = SavingsTracker
        fields = ('name',)