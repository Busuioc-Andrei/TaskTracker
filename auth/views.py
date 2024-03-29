from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy, reverse
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm

from auth.forms import NewUserForm


class SignupFormView(FormView):
    template_name = 'auth/signup.html'
    form_class = NewUserForm
    success_url = '/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Sign up was successful.')
        return super().form_valid(form)


class LoginFormView(LoginView):
    template_name = 'auth/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"You are now logged in as {form.get_user()}.")
        return super().form_valid(form)


class LogoutView(SuccessMessageMixin, RedirectView):
    pattern_name = 'index'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        messages.success(self.request, "You have successfully logged out.")
        return super().get_redirect_url(*args, **kwargs)


class ChangePasswordView(PasswordChangeView):
    template_name = 'auth/change_password.html'
    login_url = "login"

    def get_success_url(self):
        messages.success(self.request, "Password changed successfully.")
        return '/'


class ResetPasswordView(PasswordResetView):
    template_name = 'auth/reset_password.html'
    email_template_name = 'auth/reset_password_email.html'
    success_url = reverse_lazy('reset-password-done')


class ResetPasswordDoneView(PasswordResetDoneView):
    template_name = 'auth/reset_password_done.html'


class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'auth/reset_password_confirm.html'
    success_url = reverse_lazy('reset-password-complete')

    def get_success_url(self):
        messages.success(self.request, "Password changed successfully, please login.")
        return reverse('login')
