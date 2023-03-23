import uuid

from django import forms
from django.db.models import DateTimeField
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from main.forms import ColumnForm
from main.models import Issue, Board, Column
from main.widgets import XDSoftDateTimePickerInput


def add_datetime_widget(self, form):  # datetime widget for all datetime fields
    date_fields = [field.name for field in self.model._meta.get_fields() if type(field) == DateTimeField]  # noqa
    for date_field in date_fields:
        if date_field in form.fields:
            form.fields[date_field] = forms.DateTimeField(
                input_formats=['%d/%m/%Y %H:%M'],
                widget=XDSoftDateTimePickerInput(),
                required=form.fields[date_field].required
            )
    return form


class CustomListView(ListView):
    template_name = 'main/generic_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context


class CustomCreateView(CreateView):
    template_name = 'main/generic_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(self, form)
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class CustomUpdateView(UpdateView):
    template_name = 'main/generic_edit_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(self, form)
        return form


class CustomDetailView(DetailView):
    template_name = 'main/generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_object().to_dict()
        context['model_name'] = self.model.__name__
        context['data'] = data
        return context


class CustomDeleteView(DeleteView):
    template_name = 'main/generic_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(f'{self.model.__name__.lower()}-list')


class IndexPageView(TemplateView):
    template_name = "index.html"


def echo(request):
    print(request.body)
    return HttpResponse(status=201)


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

    def get(self, request, *args, **kwargs):
        view = BoardGetView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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


class BoardColumnDeleteView(CustomDeleteView):
    model = Column

    def get_success_url(self):
        return reverse_lazy('board-detail', kwargs={'pk': self.kwargs['board_pk']})


class ColumnIssueCreateView(CustomCreateView):
    model = Issue

    def form_valid(self, form):
        # add reference to column issue was created in
        column_id = self.kwargs['column_pk']
        issue = form.save(commit=False)
        issue.column = Column.objects.get(pk=column_id)
        issue.save()
        return super().form_valid(form)
