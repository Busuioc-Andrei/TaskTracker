from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit, Field, Row
from django import forms
from django.forms import ModelForm, formset_factory

from main.models import Column, Issue, Comment


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ['name']


def issue_validations(self, parent_issue, issue_id):
    if issue_id == parent_issue.id:
        self.add_error(field='parent_issue', error="Issue cannot be it's own parent.")


def epic_validations(self, issue_type):
    if issue_type == 'epic':
        self.add_error(field='parent_issue', error="Epics cannot have a parent Issue.")


def user_story_validations(self, issue_type, parent_issue):
    if issue_type == 'user_story':
        if parent_issue.issue_type != 'epic':
            self.add_error(field='parent_issue', error="User Stories can only have Epics as parents.")


def task_validations(self, issue_type, parent_issue, issue_id):
    if issue_type == 'task':
        next_parent = parent_issue.parent_issue
        for _ in range(100):
            if not next_parent:
                break
            elif next_parent.id == issue_id:
                self.add_error(field='parent_issue', error="Circular reference detected.")
                break
            next_parent = next_parent.parent_issue
        else:
            self.add_error(field='parent_issue', error="Maximum nesting depth reached.")


class IssueForm(ModelForm):
    class Meta:
        model = Issue
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        issue_id = self.instance.pk
        issue_type = cleaned_data.get("issue_type")
        parent_issue = cleaned_data.get("parent_issue")
        if issue_type and parent_issue:
            issue_validations(self, parent_issue=parent_issue, issue_id=issue_id)
            epic_validations(self, issue_type=issue_type)
            user_story_validations(self, issue_type=issue_type, parent_issue=parent_issue)
            task_validations(self, issue_type=issue_type, parent_issue=parent_issue, issue_id=issue_id)


class IssueModalForm(IssueForm, BSModalModelForm):
    pass


class IssueModalUpdateForm(IssueForm, BSModalModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=False)


class CommentForm(ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    prefix = 'comment'

    class Meta:
        model = Comment
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('description', form='comment-form'),
            # Submit('submit', 'Submit', css_class='button white'),
        )
