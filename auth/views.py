from django.contrib import messages
from django.contrib.auth import login
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from auth.forms import NewUserForm


class SignupFormView(FormView):
    template_name = 'auth/signup.html'
    form_class = NewUserForm
    success_url = '/test_app/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Registration successful.')
        return super().form_valid(form)
