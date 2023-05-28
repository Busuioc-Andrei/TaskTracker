from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Submit, Field, Row
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, formset_factory

from auth.models import User
from main.models import Column, Issue, Comment, Invitation


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ['name']


def issue_validations(self, parent_issue, issue_pk):
    if issue_pk == parent_issue.pk:
        self.add_error(field='parent_issue', error="Issue cannot be it's own parent.")


def epic_validations(self, issue_type):
    if issue_type == 'epic':
        self.add_error(field='parent_issue', error="Epics cannot have a parent Issue.")


def user_story_validations(self, issue_type, parent_issue):
    if issue_type == 'user_story':
        if parent_issue.issue_type != 'epic':
            self.add_error(field='parent_issue', error="User Stories can only have Epics as parents.")


def task_validations(self, issue_type, parent_issue, issue_pk):
    if issue_type == 'task':
        next_parent = parent_issue.parent_issue
        for _ in range(100):
            if not next_parent:
                break
            elif next_parent.pk == issue_pk:
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
        issue_pk = self.instance.pk
        issue_type = cleaned_data.get("issue_type")
        parent_issue = cleaned_data.get("parent_issue")
        if issue_type and parent_issue:
            issue_validations(self, parent_issue=parent_issue, issue_pk=issue_pk)
            epic_validations(self, issue_type=issue_type)
            user_story_validations(self, issue_type=issue_type, parent_issue=parent_issue)
            task_validations(self, issue_type=issue_type, parent_issue=parent_issue, issue_pk=issue_pk)


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
        )


class InvitationForm(ModelForm):
    sent_to = forms.CharField()

    class Meta:
        model = Invitation
        fields = ['sent_to']

    def __init__(self, permission_group, *args, **kwargs):
        self.permission_group = permission_group
        super().__init__(*args, **kwargs)

    def clean_sent_to(self):
        username = self.cleaned_data['sent_to']
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise forms.ValidationError("Invalid username.")

        existing_pending_invitation = Invitation.objects.filter(
            permission_group=self.permission_group,
            sent_to=user,
            accepted=None
        ).first()

        if existing_pending_invitation:
            raise forms.ValidationError("There is already a pending invitation sent to this user.")

        if self.permission_group.members.filter(pk=user.pk).exists():
            raise forms.ValidationError("The user is already a member of the project.")

        return user

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.permission_group = self.permission_group
        if commit:
            instance.save()
        return instance
