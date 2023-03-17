from django import forms
from django.db.models import DateTimeField
from django.forms import model_to_dict, ModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from main.models import Issue, Project
from main.widgets import XDSoftDateTimePickerInput


def add_datetime_widget(self, form):  # datetime widget for all datetime fields
    date_fields = [field.name for field in self.model._meta.get_fields() if type(field) == DateTimeField]  # noqa
    for date_field in date_fields:
        if date_field in form.fields:
            form.fields[date_field] = forms.DateTimeField(
                input_formats=['%d/%m/%Y %H:%M'],
                widget=XDSoftDateTimePickerInput()
            )
    return form


class CustomCreateView(CreateView):
    template_name = 'main/generic_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(self, form)
        return form


class CustomUpdateView(UpdateView):
    template_name = 'main/generic_edit_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(self, form)
        return form


class CustomDetailView(DetailView):
    template_name = 'main/generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = model_to_dict(self.get_object())
        context['model_name'] = self.model.__name__
        context['data'] = data
        return context


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=201)


class ProjectCreateView(CustomCreateView):
    model = Project


class ProjectDetailView(CustomDetailView):
    model = Project


class BoardPageView(ListView):
    template_name = "main/board.html"
    model = Issue


class TaskListView(ListView):
    template_name = 'main/task_list.html'
    model = Issue


class TaskDetailView(CustomDetailView):
    model = Issue


class TaskCreateView(CustomCreateView):
    model = Issue


class TaskUpdateView(CustomUpdateView):
    model = Issue


class TaskDeleteView(DeleteView):
    template_name = 'main/generic_confirm_delete.html'
    model = Issue
    success_url = reverse_lazy('task-list')
