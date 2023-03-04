from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

# from test_app.forms import TaskForm
from test_app.models import Task


def index(request):
    return HttpResponse("Hello, world.")


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
