from django.urls import path
from . import views


app_name = "budgets"

urlpatterns = [
    path('budgets/', views.BudgetList.as_view(), name='budget_list'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('rulesets', views.RulesetList.as_view(), name='rulesets'),
    path('budgets/<int:pk>/', views.BudgetDetail.as_view(), name='single_budget'),
    path('rulesets/<int:pk>/', views.RulesetDetail.as_view(), name='single_ruleset'),
    path('create_budget/', views.CreateBudget.as_view(), name="add_budget"),
    path('budgets/<int:pk>/add_budget_category/', views.CreateBudgetCategory.as_view(), name="add_budget_category"),
    path('add_category/', views.CreateCategory.as_view(), name='add_category'),
    path('rulesets/<int:pk>/add_rule/', views.CreateRule.as_view(), name='add_rule'),
    path('create_ruleset/', views.CreateRuleset.as_view(), name="add_ruleset"),
]