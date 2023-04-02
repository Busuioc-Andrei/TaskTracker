from django.urls import path

from .models import Issue, BaseModel, Project, Board, Column
from .views import CustomListView, CustomCreateView, CustomDetailView, CustomUpdateView, DeleteModalView, \
    IndexPageView, BoardPageView, echo, BoardCreateView, ColumnIssueCreateModalView, BoardColumnDeleteView, persistent, \
    IssueCreateView, IssueUpdateView

generic_models = [Issue, Project, Board, Column]


def add_generic_paths(model_types: [type[BaseModel]]):
    generic_paths = []
    for model_type in model_types:
        model_name = model_type.__name__
        mnl = model_name.lower()
        ListView = type(f'{model_name}ListView', (CustomListView,), {'model': model_type}) # noqa
        CreateView = type(f'{model_name}CreateView', (CustomCreateView,), {'model': model_type}) # noqa
        UpdateView = type(f'{model_name}UpdateView', (CustomUpdateView,), {'model': model_type}) # noqa
        DetailView = type(f'{model_name}DetailView', (CustomDetailView,), {'model': model_type}) # noqa
        DeleteView = type(f'{model_name}DeleteView', (DeleteModalView,), {'model': model_type}) # noqa
        generic_paths = generic_paths + [
            path(f'{mnl}s/', ListView.as_view(), name=f'{mnl}-list'), # noqa
            path(f'{mnl}/add/', CreateView.as_view(), name=f'{mnl}-add'), # noqa
            path(f'{mnl}/<uuid:pk>/update/', UpdateView.as_view(), name=f'{mnl}-update'), # noqa
            path(f'{mnl}/<uuid:pk>/', DetailView.as_view(), name=f'{mnl}-detail'),  # noqa
            path(f'{mnl}/<uuid:pk>/delete/', DeleteView.as_view(), name=f'{mnl}-delete') # noqa
        ]
    return generic_paths


urlpatterns = [
    path('', IndexPageView.as_view(), name='index'),
    path('echo/', echo, name='echo'),
    path('persistent/', persistent, name='persistent'),

    path('board/add/', BoardCreateView.as_view(), name='board-add'),
    path('board/<uuid:pk>/', BoardPageView.as_view(), name='board-detail'),
    path('board/<uuid:board_pk>/column/<uuid:pk>/delete/', BoardColumnDeleteView.as_view(), name='board-column-delete'),

    path('column/<uuid:column_pk>/issue/add/', ColumnIssueCreateModalView.as_view(), name='column-issue-add'),

    path('issue/add/', IssueCreateView.as_view(), name='issue-add'),
    path('issue/<uuid:pk>/update/', IssueUpdateView.as_view(), name='issue-update'),

] + add_generic_paths(generic_models)  # generic_paths won't overwrite paths already defined
