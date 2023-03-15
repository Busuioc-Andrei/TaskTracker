from django import forms
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from main.models import Issue
from main.widgets import XDSoftDateTimePickerInput


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=201)


class BoardPageView(TemplateView):
    template_name = "main/board.html"


class TaskListView(ListView):
    template_name = 'main/task_list.html'
    model = Issue


class TaskDetailView(DetailView):
    template_name = 'main/task_detail.html'
    model = Issue


class TaskCreateView(CreateView):
    template_name = 'main/task_form.html'
    model = Issue
    fields = ['name', 'description', 'issue_type', 'start_date']

    def get_form(self, form_class=None):
        form = super(TaskCreateView, self).get_form(form_class)
        form.fields['start_date'] = forms.DateTimeField(
            input_formats=['%d/%m/%Y %H:%M'],
            widget=XDSoftDateTimePickerInput()
        )
        return form


class TaskUpdateView(UpdateView):
    template_name = 'main/task_form.html'
    model = Issue
    fields = ['name', 'description']


class TaskDeleteView(DeleteView):
    template_name = 'main/task_confirm_delete.html'
    model = Issue
    success_url = reverse_lazy('task-list')
