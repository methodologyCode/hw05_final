from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    """Обработка входа"""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change/done/')


class PasswordResetView(PasswordContextMixin, FormView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset/done/')


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    success_url = reverse_lazy('reset/done/')
