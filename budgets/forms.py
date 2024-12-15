from django import forms
from .models import Category, Budget, BudgetCategory, Ruleset, Rule


class DateInput(forms.DateInput):
    input_type = 'date'


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('title', )


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