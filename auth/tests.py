from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from auth.models import User


class ChangePasswordTest(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='user1', password='testpass1')
        self.client = Client()
        self.client.force_login(self.user1)

    def test_change_password(self):
        response = self.client.post(reverse('change-password'), {
            'old_password': 'testpass1',
            'new_password1': 'new_password',
            'new_password2': 'new_password'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password changed successfully.')

    def test_reset_password(self):
        response = self.client.get(reverse('reset-password'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password Reset')

        response = self.client.post(reverse('reset-password'), {'email': 'user1@example.com'})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset')
        self.assertIn('user1@example.com', mail.outbox[0].to)