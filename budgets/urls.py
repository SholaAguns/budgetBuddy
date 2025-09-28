from django.urls import path
from . import views


app_name = "budgets"

urlpatterns = [
    path('', views.BudgetList.as_view(), name='budget_list'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('rulesets', views.RulesetList.as_view(), name='rulesets'),
    path('savings', views.SavingsTrackerList.as_view(), name='savings_tracker_list'),
    path('budget/<int:pk>/', views.BudgetDetail.as_view(), name='single_budget'),
    path('ruleset/<int:pk>/', views.RulesetDetail.as_view(), name='single_ruleset'),
    path('savings_tracker/<int:pk>', views.SavingsTrackerDetail.as_view(), name='savings_tracker_detail'),
    path('create_budget/', views.CreateBudget.as_view(), name="add_budget"),
    path('add_savings_tracker/', views.CreateSavingsTracker.as_view(), name='add_savings_tracker'),
    path('budget/<int:pk>/add_budget_category/', views.CreateBudgetCategory.as_view(), name="add_budget_category"),
    path('budget/<int:pk>/update', views.BudgetUpdate.as_view(), name='update_budget'),
    path('update_savings_tracker/<int:pk>', views.UpdateSavingsTracker.as_view(), name='update_savings_tracker'),
    path('savings_tracker/<int:pk>/update_name', views.UpdateSavingsTrackerName.as_view(), name='update_savings_tracker_name'),
    path('budget/<int:pk>/delete', views.DeleteBudget.as_view(), name='delete_budget'),
    path('add_category/', views.CreateCategory.as_view(), name='add_category'),
    path('ruleset/<int:pk>/add_rule/', views.CreateRule.as_view(), name='add_rule'),
    path('create_ruleset/', views.CreateRuleset.as_view(), name="add_ruleset"),
    path('ruleset/<int:pk>/update', views.RulesetUpdate.as_view(), name='update_ruleset'),
    path('ruleset/<int:pk>/delete', views.DeleteRuleset.as_view(), name='delete_ruleset'),
    path('delete_category/<int:pk>', views.category_remove, name='delete_category'),
    path('delete_rule/<int:pk>', views.rule_remove, name='delete_rule'),
    path('delete_savings_tracker/<int:pk>',views.DeleteSavingsTracker.as_view(), name='delete_savings_tracker'),
    path('delete_budget_category/<int:pk>', views.budgetcategory_remove, name='delete_budget_category'),
    path('budget/<int:pk>/duplicate', views.budget_duplicate, name='duplicate_budget'),
    path('ruleset/<int:pk>/duplicate', views.ruleset_duplicate, name='duplicate_ruleset'),
    path('category/<int:pk>/update', views.CategoryUpdate.as_view(), name='update_category'),
    path('budget_category/<int:pk>/update', views.BudgetCategoryUpdate.as_view(), name='update_budget_category'),
    path('savings_tracker/<int:pk>/update_savings', views.update_savings, name='update_savings'),
    path('savings_tracker/<int:pk>/quick_update', views.quick_update_savings, name='quick_update_savings'),
    path('savings_tracker/<int:pk>/ajax_update', views.ajax_update_balance, name='ajax_update_balance'),
    path('budget/<int:pk>/toggle_archive', views.toggle_archive_budget, name='toggle_archive_budget'),
    path('bulk_archive_budgets/', views.bulk_archive_budgets, name='bulk_archive_budgets'),
    path('bulk_unarchive_budgets/', views.bulk_unarchive_budgets, name='bulk_unarchive_budgets'),
    path('bulk_delete_budgets/', views.bulk_delete_budgets, name='bulk_delete_budgets')
]