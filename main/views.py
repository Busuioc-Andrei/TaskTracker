from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView
from bootstrap_modal_forms.utils import is_ajax
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, DeleteViewCustomDeleteWarning
from rules.contrib.views import AutoPermissionRequiredMixin

from auth.models import User
from commons.mixins import ModelNameMixin, DatetimePickerMixin, ModelChoiceFilterMixin
from commons.utils import parse_jquery_sortable, order_columns, order_issues
from main.forms import ColumnForm, IssueModalForm, IssueForm, IssueModalUpdateForm, CommentForm, InvitationForm, \
    UserAndProfileForm, SprintModalForm, SprintCompleteModalForm
from main.models import Issue, Board, Column, Comment, Project, Invitation, PermissionGroup, Profile, Sprint

import warnings

warnings.filterwarnings(action='ignore', category=DeleteViewCustomDeleteWarning)


class CustomListView(LoginRequiredMixin, ModelNameMixin, ListView):
    template_name = 'generic/generic_list.html'

    def get_queryset(self):
        user = self.request.user
        filtered_queryset = self.model.filter_visible_items(user)
        return filtered_queryset


class CustomCreateView(LoginRequiredMixin, ModelNameMixin, ModelChoiceFilterMixin, DatetimePickerMixin, CreateView):
    template_name = 'generic/generic_form.html'
    fields = '__all__'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class CustomUpdateView(LoginRequiredMixin, AutoPermissionRequiredMixin, ModelNameMixin, ModelChoiceFilterMixin, DatetimePickerMixin, UpdateView):
    template_name = 'generic/generic_edit_form.html'
    fields = '__all__'

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class CustomDetailView(LoginRequiredMixin, AutoPermissionRequiredMixin, ModelNameMixin, DetailView):
    template_name = 'generic/generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_object().to_dict()
        context['data'] = data
        return context


class CustomDeleteView(LoginRequiredMixin, AutoPermissionRequiredMixin, ModelNameMixin, DeleteView):
    template_name = 'generic/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(f'{self.model.__name__.lower()}-list')


class DeleteModalView(CustomDeleteView, BSModalDeleteView):
    template_name = 'modal/modal_confirm_delete.html'

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(super().get_success_url())

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=204)


def empty(request):
    if request.method == 'GET':
        return HttpResponse(200)


def persistent(request):
    sortable_data = parse_jquery_sortable(request.body)
    if sortable_data:
        order_columns(sortable_data)
        order_issues(sortable_data)

    return HttpResponse(status=204)


@require_POST
def move_issue_to_board(request):
    issue_id = request.POST.get('issueId')
    board_id = request.POST.get('boardId')

    issue = get_object_or_404(Issue, id=issue_id)
    board = get_object_or_404(Board, id=board_id)

    todo_column = Column.objects.filter(board=board, name='To Do').first()
    if todo_column:
        issue.column = todo_column
        issue.save()

        return JsonResponse({'message': 'Column ID updated successfully'})
    else:
        return JsonResponse({'message': 'Failed to update Column ID'}, status=400)


class ProjectPageView(CustomDetailView):
    template_name = "main/project.html"
    model = Project

    def get(self, request, *args, **kwargs):
        project = Project.objects.get(pk=kwargs["pk"])
        self.request.user.profile.current_project = project  # noqa
        self.request.user.profile.save()  # noqa
        return super().get(request, *args, **kwargs)


class BoardGetView(CustomDetailView):
    template_name = "main/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ColumnForm()
        return context


class BoardColumnPostView(CustomCreateView):
    template_name = "main/board.html"
    form_class = ColumnForm
    model = Column
    fields = None

    def form_valid(self, form):
        form.instance.board_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('board-detail', kwargs={'pk': self.kwargs['pk']})


class BoardPageView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        view = BoardGetView.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        view = BoardColumnPostView.as_view()
        return view(request, *args, **kwargs)


class BoardCreateView(CustomCreateView):
    model = Board

    def form_valid(self, form):
        board = form.save()
        # add default columns
        Column.objects.bulk_create([
            Column(name='To Do', board=board, created_by=self.request.user, modified_by=self.request.user),
            Column(name='In Progress', board=board, created_by=self.request.user, modified_by=self.request.user),
            Column(name='Done', board=board, created_by=self.request.user, modified_by=self.request.user),
        ])
        return super().form_valid(form)


class BoardColumnDeleteView(DeleteModalView):
    model = Column


class BoardIssueDeleteView(DeleteModalView):
    model = Issue


class IssueCommentDeleteView(DeleteModalView):
    model = Comment


class ColumnIssueCreateModalView(CustomCreateView, BSModalCreateView):
    model = Issue
    template_name = 'main/modal/issue_form_modal.html'
    form_class = IssueModalForm
    fields = None  # set to None because a Form Class is used

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            # add reference to column issue was created in
            column_pk = self.kwargs['column_pk']
            issue = form.save(commit=False)
            issue.column = Column.objects.get(pk=column_pk)
            issue.save()
        return super().form_valid(form)

    def get_success_url(self):
        column = Column.objects.get(pk=self.kwargs['column_pk'])
        return reverse_lazy('board-detail', kwargs={'pk': column.board_id})


class IssueCreateView(CustomCreateView):
    model = Issue
    form_class = IssueForm
    fields = None


class IssueUpdateView(CustomUpdateView):
    model = Issue
    form_class = IssueForm
    fields = None


class BoardIssueUpdateModalView(CustomUpdateView, BSModalUpdateView):
    model = Issue
    template_name = 'main/modal/issue_edit_modal.html'
    form_class = IssueModalUpdateForm
    fields = None

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            form.save()
        return super().form_valid(form)

    # def form_invalid(self, form):
    #     print(form.errors)
    #     return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm(prefix='comment')

        issue_pk = self.kwargs['pk']
        issue = Issue.objects.get(pk=issue_pk)

        context['comments'] = issue.comment_set.all()
        return context

    def post(self, request, *args, **kwargs):
        if 'comment_submit' in request.POST and not is_ajax(self.request.META):
            return IssueCommentCreateView.as_view()(request, *args, **kwargs)
        else:
            return super().post(request, *args, **kwargs)


class IssueDetailView(CustomDetailView):
    model = Issue


class IssueCommentCreateView(CustomCreateView):
    model = Comment
    form_class = CommentForm
    fields = None

    def form_valid(self, form):
        if not form.cleaned_data['description'].strip():
            form.add_error('description', "Comment can't be empty")
            return self.form_invalid(form)

        if not is_ajax(self.request.META):
            comment = form.save(commit=False)
            comment.created_by = self.request.user
            comment.modified_by = self.request.user

            issue_pk = self.kwargs['pk']
            comment.issue = Issue.objects.get(pk=issue_pk)
            comment.save()
        return HttpResponse(status=200)


class CustomizeView(LoginRequiredMixin, TemplateView):
    model = Project
    template_name = 'main/customize.html'


class InviteCreateView(CustomCreateView):
    model = Invitation
    form_class = InvitationForm
    fields = None

    def get_success_url(self):
        project_pk = self.kwargs['project_pk']
        return reverse_lazy('project-detail', kwargs={'pk': project_pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project_pk = self.kwargs['project_pk']
        project = Project.objects.get(pk=project_pk)
        kwargs['permission_group'] = project.permission_group
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Invitation sent successfully!')
        return super().form_valid(form)


class InvitationAcceptView(CustomUpdateView):
    model = Invitation
    fields = []

    def form_valid(self, form):
        form.instance.accepted = True
        form.instance.permission_group.members.add(form.instance.sent_to)
        messages.success(self.request, f'Successfully joined project {form.instance.permission_group.project.name}!')
        return super().form_valid(form)

    def get_success_url(self):
        project = self.object.permission_group.project
        return reverse_lazy('project-detail', kwargs={'pk': project.pk})


class InvitationRejectView(CustomUpdateView):
    model = Invitation
    fields = []

    def form_valid(self, form):
        form.instance.accepted = False
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class RemoveMemberView(DeleteModalView):
    model = User

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            member = self.get_object()
            permission_group = PermissionGroup.objects.get(pk=self.kwargs['group_pk'])
            permission_group.members.remove(member)

        return HttpResponseRedirect(super().get_success_url())


class ProfileDetailView(CustomDetailView):
    model = Profile
    template_name = 'main/profile_detail.html'


class ProfileUpdateView(CustomUpdateView):
    model = User
    form_class = UserAndProfileForm
    fields = None
    template_name = 'main/profile_edit_form.html'

    def get_success_url(self):
        return reverse_lazy('profile-detail', kwargs={'pk': self.kwargs['pk']})


class SprintCreateModalView(CustomCreateView, BSModalCreateView):
    model = Sprint
    template_name = 'main/modal/sprint_form_modal.html'
    form_class = SprintModalForm
    fields = None

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            sprint = form.save()
            project = sprint.project
            project.current_sprint = sprint
            project.save()
            return super().form_valid(form)
        else:
            return HttpResponse(status=200)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project_pk = self.kwargs['project_pk']
        project = Project.objects.get(pk=project_pk)
        kwargs['initial']['project'] = project
        return kwargs

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.kwargs['project_pk']})


class SprintCompleteModalView(CustomUpdateView, BSModalUpdateView):
    model = Sprint
    template_name = 'main/modal/sprint_complete_modal.html'
    form_class = SprintCompleteModalForm
    fields = None

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            sprint = form.save()
            sprint.project.current_sprint = None
            sprint.project.save()

            sprint.project.issue_set.update(column_id=None)
            sprint.project.issue_set.filter(done=False).update(in_backlog=True)
            return super().form_valid(form)
        else:
            return HttpResponse(status=200)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
