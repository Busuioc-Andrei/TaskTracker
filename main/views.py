from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from main.models import Task


class IndexPageView(TemplateView):
    template_name = "index.html"


class TaskListView(ListView):
    model = Task


class TaskDetailView(DetailView):
    model = Task


class TaskCreateView(CreateView):
    model = Task
    fields = ['name', 'description']


class TaskUpdateView(UpdateView):
    model = Task
    fields = ['name', 'description']


class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('task-list')
