import json

from django import forms
from django.db.models import DateTimeField
from commons.widgets import XDSoftDateTimePickerInput
from main.models import Column, Issue


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


def parse_jquery_sortable(sortable_data_binary):
    sortable_data = json.loads(sortable_data_binary.decode())
    sortable_data_split = sortable_data['data'].split('&')

    parsed_data = []
    for data in sortable_data_split:
        data_split = data.split('[]=')
        if data_split[0]:
            column, row = data_split
            parsed_data.append({'column': column, 'row': row})

    sortable_data['data'] = parsed_data
    return sortable_data


def order_columns(sortable_data):
    if sortable_data['sortedItem'] == 'column':
        for idx, data in enumerate(sortable_data['data']):
            column = Column.objects.get(pk=data['row'])
            column.order = idx
            column.save()


def order_issues(sortable_data):
    if sortable_data['sortedItem'] == 'issue':
        new_column = None
        moved_issue = None
        if 'newColumn' in sortable_data and 'movedIssue' in sortable_data:
            new_column = sortable_data['newColumn'].split('_')[1]
            moved_issue = sortable_data['movedIssue'].split('_')[1]
        for idx, data in enumerate(sortable_data['data']):
            issue = Issue.objects.get(pk=data['row'])
            issue.order = idx
            if data['row'] == moved_issue:
                column = Column.objects.get(pk=new_column)
                issue.column = column
            issue.save()
