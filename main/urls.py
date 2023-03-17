from django.urls import path

from .views import TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskDetailView, IndexPageView, \
    BoardPageView, echo, ProjectCreateView

urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),
    path('echo/', echo, name='echo'),
    path('board/', BoardPageView.as_view(), name='board'),
    path('project/add/', ProjectCreateView.as_view(), name='project-add'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('task/<uuid:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('task/add/', TaskCreateView.as_view(), name='task-add'),
    path('task/<uuid:pk>/update', TaskUpdateView.as_view(), name='task-update'),
    path('task/<uuid:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
]