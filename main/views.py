from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView
from bootstrap_modal_forms.utils import is_ajax
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, DeleteViewCustomDeleteWarning, FormMixin

from commons.mixins import ModelNameMixin, DatetimePickerMixin
from commons.utils import parse_jquery_sortable, order_columns, order_issues
from main.forms import ColumnForm, IssueModalForm, IssueForm, IssueModalUpdateForm, CommentForm
from main.models import Issue, Board, Column, Comment, Project

import warnings
warnings.filterwarnings(action='ignore', category=DeleteViewCustomDeleteWarning)


class CustomListView(ListView, ModelNameMixin):
    template_name = 'generic/generic_list.html'


class CustomCreateView(CreateView, ModelNameMixin, DatetimePickerMixin):
    template_name = 'generic/generic_form.html'
    fields = '__all__'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class CustomUpdateView(UpdateView, ModelNameMixin, DatetimePickerMixin):
    template_name = 'generic/generic_edit_form.html'
    fields = '__all__'


class CustomDetailView(DetailView, ModelNameMixin):
    template_name = 'generic/generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_object().to_dict()
        context['data'] = data
        return context


class CustomDeleteView(DeleteView, ModelNameMixin):
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


class SetCurrentProject(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        project = Project.objects.get(pk=kwargs["pk"])
        self.request.user.profile.current_project = project # noqa
        self.request.user.save()
        messages.success(self.request, "Updated current project")
        self.url = self.request.META['HTTP_REFERER']
        return super().get_redirect_url(*args, **kwargs)


class BoardGetView(DetailView):
    template_name = "main/board.html"
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ColumnForm()
        return context


class BoardColumnPostView(CreateView):
    template_name = "main/board.html"
    form_class = ColumnForm
    model = Column

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
    template_name = 'main/issue_form_modal.html'
    form_class = IssueModalForm
    fields = None  # set to None because a Form Class is used

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            # add reference to column issue was created in
            column_id = self.kwargs['column_pk']
            issue = form.save(commit=False)
            issue.column = Column.objects.get(pk=column_id)
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
    template_name = 'main/issue_edit_modal.html'
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

        issue_id = self.kwargs['pk']
        issue = Issue.objects.get(pk=issue_id)

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

            issue_id = self.kwargs['pk']
            comment.issue = Issue.objects.get(pk=issue_id)
            comment.save()
        return HttpResponse(status=200)


class CustomizeView(TemplateView):
    model = Project
    template_name = 'main/customize.html'
