from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.messages.views import SuccessMessageMixin
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


class LoginFormView(FormView):
    template_name = 'auth/login.html'
    form_class = AuthenticationForm
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(self.request, f"You are now logged in as {username}.")
            return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class LogoutView(SuccessMessageMixin, RedirectView):
    pattern_name = 'index'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        messages.success(self.request, "You have successfully logged out.")
        return super().get_redirect_url(*args, **kwargs)
