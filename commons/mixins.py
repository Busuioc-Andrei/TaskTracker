from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin

from commons.utils import add_datetime_widget


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
