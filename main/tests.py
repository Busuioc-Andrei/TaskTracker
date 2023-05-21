from django.test import Client, TestCase
from django.urls import reverse

from auth.models import User
from main.forms import IssueForm
from main.models import Issue, Project


class IssueFormTestCase(TestCase):
    def setUp(self) -> None:
        project = Project.objects.create(name='test_project')
        Issue.objects.create(name='test_task', issue_type='task', project=project)
        Issue.objects.create(name='test_task2', issue_type='task', project=project)
        Issue.objects.create(name='test_task3', issue_type='task', project=project)
        Issue.objects.create(name='test_user_story', issue_type='user_story', project=project)
        Issue.objects.create(name='test_epic', issue_type='epic', project=project)

    def test_issue_cannot_reference_itself(self):
        task = Issue.objects.get(name='test_task')

        form = IssueForm(instance=task)
        data = {
            'parent_issue': task.id
        }
        form = IssueForm(instance=task, data={**form.initial, **data})

        self.assertFormError(form, 'parent_issue', "Issue cannot be it's own parent.")

    def test_user_story_cannot_have_non_epic_parent(self):
        project = Project.objects.get(name='test_project')
        task = Issue.objects.get(name='test_task')
        user_story = Issue.objects.get(name='test_user_story')
        epic = Issue.objects.get(name='test_epic')

        user_story_data = {'name': 'test_user_story1', 'issue_type': 'user_story', 'parent_issue': task.id, 'project': project.id}
        form = IssueForm(data=user_story_data)
        self.assertFormError(form, 'parent_issue', "User Stories can only have Epics as parents.")

        user_story_data['parent_issue'] = user_story
        form = IssueForm(data=user_story_data)
        self.assertFormError(form, 'parent_issue', "User Stories can only have Epics as parents.")

        user_story_data['parent_issue'] = epic
        form = IssueForm(data=user_story_data)
        self.assertTrue(form.is_valid())

    def test_reject_circular_references(self):
        task = Issue.objects.get(name='test_task')
        task2 = Issue.objects.get(name='test_task2')
        task3 = Issue.objects.get(name='test_task3')

        form = IssueForm(instance=task)
        data = {
            'parent_issue': task2.id
        }
        form = IssueForm(instance=task, data={**form.initial, **data})
        self.assertTrue(form.is_valid())
        form.save()

        form = IssueForm(instance=task2)
        data = {
            'parent_issue': task3.id
        }
        form = IssueForm(instance=task2, data={**form.initial, **data})
        self.assertTrue(form.is_valid())
        form.save()

        form = IssueForm(instance=task3)
        data = {
            'parent_issue': task.id
        }
        form = IssueForm(instance=task3, data={**form.initial, **data})
        self.assertFormError(form, 'parent_issue', "Circular reference detected.")

    def test_epic_cannot_have_parent(self):
        """An epic can't have a parent"""
        project = Project.objects.get(name='test_project')
        task = Issue.objects.get(name='test_task')

        epic_data = {'name': 'test_epic1', 'issue_type': 'epic', 'parent_issue': task.id, 'project': project.id}
        form = IssueForm(data=epic_data)

        self.assertFormError(form, 'parent_issue', 'Epics cannot have a parent Issue.')


class ProjectVisibilityTestCase(TestCase):  # this test should be modified when implementing project groups
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='user1', password='testpass1')
        self.user2 = User.objects.create_user(username='user2', password='testpass2')

    def test_project_details_visible_only_to_creator(self):
        client = Client()
        client.force_login(self.user1)
        project = Project.objects.create(name='test_project', created_by=self.user1)
        response = client.get(reverse('project-detail', kwargs={'pk': project.id}))
        self.assertEqual(response.status_code, 200)

        client.force_login(self.user2)
        response = client.get(reverse('project-detail', kwargs={'pk': project.id}))
        self.assertEqual(response.status_code, 403)
