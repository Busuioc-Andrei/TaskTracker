from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin

from commons.utils import add_datetime_widget, add_model_choice_filter


class DatetimePickerMixin(FormMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_datetime_widget(form)
        return form


class ModelNameMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model.__name__ # noqa
        context['model_verbose_name'] = self.model._meta.verbose_name.title()  # noqa
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural.title()  # noqa
        return context


class ModelChoiceFilterMixin(FormMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form = add_model_choice_filter(self, form)
        return form
