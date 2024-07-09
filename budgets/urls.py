from django.urls import path
from . import views


app_name = "budgets"

urlpatterns = [
    path('', views.BudgetList.as_view(), name='budget_list'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('rulesets', views.RulesetList.as_view(), name='rulesets'),
    path('budget/<int:pk>/', views.BudgetDetail.as_view(), name='single_budget'),
    path('ruleset/<int:pk>/', views.RulesetDetail.as_view(), name='single_ruleset'),
    path('create_budget/', views.CreateBudget.as_view(), name="add_budget"),
    path('budget/<int:pk>/add_budget_category/', views.CreateBudgetCategory.as_view(), name="add_budget_category"),
    path('budget/<int:pk>/update', views.BudgetUpdate.as_view(), name='update_budget'),
    path('budget/<int:pk>/delete', views.DeleteBudget.as_view(), name='delete_budget'),
    path('add_category/', views.CreateCategory.as_view(), name='add_category'),
    path('ruleset/<int:pk>/add_rule/', views.CreateRule.as_view(), name='add_rule'),
    path('create_ruleset/', views.CreateRuleset.as_view(), name="add_ruleset"),
    path('ruleset/<int:pk>/update', views.RulesetUpdate.as_view(), name='update_ruleset'),
    path('ruleset/<int:pk>/delete', views.DeleteRuleset.as_view(), name='delete_ruleset'),
    path('delete_category/<int:pk>', views.category_remove, name='delete_category'),
    path('delete_rule/<int:pk>', views.rule_remove, name='delete_rule'),
    path('delete_budget_category/<int:pk>', views.budgetcategory_remove, name='delete_budget_category'),
    path('budget/<int:pk>/duplicate', views.budget_duplicate, name='duplicate_budget'),
    path('ruleset/<int:pk>/duplicate', views.ruleset_duplicate, name='duplicate_ruleset'),
]