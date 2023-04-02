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
    if not sortable_data['data']:
        return {}

    sortable_data_split = sortable_data['data'].split('&')
    del sortable_data['data']

    sortable_data['order'] = []
    for data in sortable_data_split:
        data_split = data.split('[]=')
        sorted_item, item = data_split
        sortable_data['sortedItem'] = sorted_item
        sortable_data['order'].append(item)

    if sortable_data['sortedItem'] == 'issue':
        moved_issue = None
        new_column = None
        if 'movedIssue' in sortable_data and 'newColumn' in sortable_data:
            moved_issue = sortable_data['movedIssue'].split('_')[1]
            new_column = sortable_data['newColumn'].split('_')[1]
        sortable_data['movedIssue'] = moved_issue
        sortable_data['newColumn'] = new_column

    return sortable_data


def order_columns(sortable_data):
    if sortable_data['sortedItem'] == 'column':
        for idx, item in enumerate(sortable_data['order']):
            column = Column.objects.get(pk=item)
            column.order = idx
            column.save()


def order_issues(sortable_data):
    if sortable_data['sortedItem'] == 'issue':
        for idx, item in enumerate(sortable_data['order']):
            issue = Issue.objects.get(pk=item)
            issue.order = idx
            if item == sortable_data['movedIssue']:
                column = Column.objects.get(pk=sortable_data['newColumn'])
                issue.column = column
            issue.save()
