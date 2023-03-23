from django.forms import ModelForm

from main.models import Column


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ['name']