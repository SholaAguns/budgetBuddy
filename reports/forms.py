from django import forms
from django.core.exceptions import ValidationError
from budgets.models import Ruleset, Budget
from .models import Transaction, Report


class DateInput(forms.DateInput):
    input_type = 'date'


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('name', 'start_date', 'end_date', 'transaction_sheet')
        widgets = {'start_date':  DateInput(), 'end_date':  DateInput()}

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError('Start date cannot be greater than end date.')

        return cleaned_data


class AddRulesetForm(forms.Form):
    ruleset = forms.ModelChoiceField(queryset=None, label='Select Ruleset')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ruleset'].queryset = Ruleset.objects.filter(user=user)


class AddBudgetForm(forms.Form):
    budget = forms.ModelChoiceField(queryset=None, label='Select Budget')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['budget'].queryset = Budget.objects.filter(user=user)


class ReportNotesForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['notes']