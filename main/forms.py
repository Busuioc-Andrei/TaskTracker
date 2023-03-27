from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import ModelForm

from main.models import Column, Issue


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ['name']


class IssueModalModelForm(BSModalModelForm):
    class Meta:
        model = Issue
        fields = '__all__'
