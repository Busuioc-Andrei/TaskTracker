from django.urls import path

from .models import Issue, BaseModel, Project, Board, Column, Comment, ColorLabel, PermissionGroup
from .views import CustomListView, CustomCreateView, CustomDetailView, CustomUpdateView, DeleteModalView, \
    IndexPageView, BoardPageView, echo, BoardCreateView, ColumnIssueCreateModalView, BoardColumnDeleteView, persistent, \
    IssueCreateView, BoardIssueUpdateModalView, IssueUpdateView, empty, IssueCommentCreateView, BoardIssueDeleteView, \
    IssueCommentDeleteView, CustomizeView, ProjectPageView, InviteCreateView, InvitationRejectView, \
    InvitationAcceptView, RemoveMemberView

generic_models = [Issue, Project, Board, Column, Comment, ColorLabel]


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
    path('empty/', empty, name='empty'),
    path('persistent/', persistent, name='persistent'),

    path('customize/', CustomizeView.as_view(), name='customize'),

    path('project/<uuid:pk>/', ProjectPageView.as_view(), name='project-detail'),
    path('project/<uuid:project_pk>/invite/add/', InviteCreateView.as_view(), name='invite-add'),

    path('board/add/', BoardCreateView.as_view(), name='board-add'),
    path('board/<uuid:pk>/', BoardPageView.as_view(), name='board-detail'),
    path('board/column/<uuid:pk>/delete/', BoardColumnDeleteView.as_view(), name='board-column-delete'),
    path('board/issue/<uuid:pk>/update/', BoardIssueUpdateModalView.as_view(), name='board-issue-update'),
    path('board/issue/<uuid:pk>/delete/', BoardIssueDeleteView.as_view(), name='board-issue-delete'),

    path('column/<uuid:column_pk>/issue/add/', ColumnIssueCreateModalView.as_view(), name='column-issue-add'),

    path('issue/add/', IssueCreateView.as_view(), name='issue-add'),
    path('issue/<uuid:pk>/update/', IssueUpdateView.as_view(), name='issue-update'),
    path('issue/<uuid:pk>/comment/add/', IssueCommentCreateView.as_view(), name='issue-comment-add'),
    path('comment/<uuid:pk>/delete/', IssueCommentDeleteView.as_view(), name='issue-comment-delete'),

    path('invitation/<uuid:pk>/accept/', InvitationAcceptView.as_view(), name='invitation-accept'),
    path('invitation/<uuid:pk>/reject/', InvitationRejectView.as_view(), name='invitation-reject'),

    path('permissiongroup/<uuid:group_pk>/member/remove/<uuid:pk>/', RemoveMemberView.as_view(), name='remove-member'),

] + add_generic_paths(generic_models)  # generic_paths won't overwrite paths already defined
