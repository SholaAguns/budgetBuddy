from django.urls import reverse_lazy
from django.views.generic import TemplateView


class Index(TemplateView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'reports/index.html'


