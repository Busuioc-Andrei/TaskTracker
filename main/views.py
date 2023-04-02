from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView
from bootstrap_modal_forms.utils import is_ajax
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, DeleteViewCustomDeleteWarning, FormMixin

from commons.utils import add_datetime_widget, parse_jquery_sortable, order_columns, order_issues
from main.forms import ColumnForm, IssueModalModelForm
from main.models import Issue, Board, Column

import warnings
warnings.filterwarnings(action='ignore', category=DeleteViewCustomDeleteWarning)


class DatetimePickerMixin(FormMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(self, form) # noqa
        return form


class ModelNameMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__ # noqa
        return context


class CustomListView(ListView, ModelNameMixin):
    template_name = 'main/generic_list.html'


class CustomCreateView(CreateView, ModelNameMixin, DatetimePickerMixin):
    template_name = 'main/generic_form.html'
    fields = '__all__'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class CustomUpdateView(UpdateView, ModelNameMixin, DatetimePickerMixin):
    template_name = 'main/generic_edit_form.html'
    fields = '__all__'


class CustomDetailView(DetailView, ModelNameMixin):
    template_name = 'main/generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_object().to_dict()
        context['data'] = data
        return context


class CustomDeleteView(DeleteView, ModelNameMixin):
    template_name = 'main/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(f'{self.model.__name__.lower()}-list')


class DeleteModalView(CustomDeleteView, BSModalDeleteView):
    template_name = 'main/modal_confirm_delete.html'

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(super().get_success_url())


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=204)


def persistent(request):
    sortable_data = parse_jquery_sortable(request.body)
    if sortable_data:
        order_columns(sortable_data)
        order_issues(sortable_data)

    return HttpResponse(status=204)


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

    def get_success_url(self):
        return reverse_lazy('board-detail', kwargs={'pk': self.kwargs['board_pk']})


class ColumnIssueCreateModalView(CustomCreateView, BSModalCreateView):
    model = Issue
    template_name = 'main/issue_form_modal.html'
    fields = None  # set to None because a Form Class is used
    form_class = IssueModalModelForm

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
