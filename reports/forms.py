from django import forms

from budgets.models import Ruleset, Budget
from .models import Transaction, Report


class DateInput(forms.DateInput):
    input_type = 'date'


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('name', 'start_date', 'end_date', 'transaction_sheet')
        widgets = {'start_date':  DateInput(), 'end_date':  DateInput()}


class AddRulesetForm(forms.Form):
    ruleset = forms.ModelChoiceField(queryset=Ruleset.objects.all(), label='Select Ruleset')


class AddBudgetForm(forms.Form):
    budget = forms.ModelChoiceField(queryset=Budget.objects.all(), label='Select Budget')