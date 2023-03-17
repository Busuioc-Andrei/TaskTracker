from django import forms
from django.db.models import DateTimeField
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from main.models import Issue, Project
from main.widgets import XDSoftDateTimePickerInput


class CustomCreateView(CreateView):
    template_name = 'main/generic_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        date_fields = [field.name for field in self.model._meta.get_fields() if type(field) == DateTimeField] # noqa
        for date_field in date_fields:
            if date_field in form.fields:
                form.fields[date_field] = forms.DateTimeField(
                    input_formats=['%d/%m/%Y %H:%M'],
                    widget=XDSoftDateTimePickerInput()
                )
        return form


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=201)


class ProjectCreateView(CustomCreateView):
    model = Project


class BoardPageView(ListView):
    template_name = "main/board.html"
    model = Issue


class TaskListView(ListView):
    template_name = 'main/task_list.html'
    model = Issue


class TaskDetailView(DetailView):
    template_name = 'main/task_detail.html'
    model = Issue


class TaskCreateView(CustomCreateView):
    model = Issue


class TaskUpdateView(UpdateView):
    template_name = 'main/generic_form.html'
    model = Issue
    fields = ['name', 'description']


class TaskDeleteView(DeleteView):
    template_name = 'main/task_confirm_delete.html'
    model = Issue
    success_url = reverse_lazy('task-list')
