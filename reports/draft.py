from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from .models import Transaction, Report
from .forms import TransactionForm

def add_multiple_transactions(request, report_id):
    report = Report.objects.get(id=report_id)
    TransactionFormSet = modelformset_factory(Transaction, form=TransactionForm, extra=3)
    # extra=3 means display 3 empty forms by default

    if request.method == 'POST':
        formset = TransactionFormSet(request.POST, request.FILES, queryset=Transaction.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.report = report
                instance.save()
            return redirect('reports:report_detail', pk=report.id)
    else:
        formset = TransactionFormSet(queryset=Transaction.objects.none())

    return render(request, 'add_multiple_transactions.html', {
        'formset': formset,
        'report': report,
    })
