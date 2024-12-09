from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

from .views import add_transactions

app_name = "reports"

urlpatterns = [
    path('', views.ReportList.as_view(), name='report_list'),
    path('create_report/', views.CreateReport.as_view(), name='add_report'),
    path('report/<int:pk>/', views.ReportDetail.as_view(), name='single_report'),
    path('report/<int:pk>/update', views.ReportUpdate.as_view(), name='update_report'),
    path('report/<int:pk>/delete', views.DeleteReport.as_view(), name='delete_report'),
    path('report/<int:pk>/import_transactions', views.add_transactions, name='add_transactions'),
    path('report/<int:pk>/clear_transactions', views.delete_transactions, name='clear_transactions'),
    path('report/<int:pk>/add_budget', views.add_budget, name='add_budget'),
    path('report/<int:pk>/add_ruleset', views.add_ruleset, name='add_ruleset'),
    path('report/<int:pk>/add_notes', views.update_report_notes, name='update_report_notes'),
    path('report/<int:pk>/pdf', views.ReportPDFView.as_view(), name='generate_pdf'),
    path('report/<int:pk>/add_transaction', views.CreateTransaction.as_view(), name='add_transaction')
    #path('report/<int:pk>/import_transactions', views.add_transactions, name='add_transactions'),
]