from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView
from . import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from django.urls import reverse
from django.contrib import messages


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'



def delete_user_confirm(request):
    user = request.user

    if request.method == 'POST':
        user.delete()
        return redirect('home')
    else:
        return render(request, 'accounts/user_confirm_delete.html')



