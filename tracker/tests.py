from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import ActivityEntry

class TimeSaverTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        now = timezone.now()
        ActivityEntry.objects.create(
            user=self.user,
            category='Учёба',
            start=now - timedelta(hours=2),
            end=now,
            note='Учился Django'
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # Проверяем, что totals присутствуют в контексте
        self.assertIn('data', response.context)

    def test_add_entry_view(self):
        now = timezone.now()
        response = self.client.post(reverse('entry_add'), {
            'category': 'Отдых',
            'start': (now - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'end': now.strftime('%Y-%m-%dT%H:%M'),
            'note': 'Отдыхал'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ActivityEntry.objects.filter(user=self.user).count(), 2)

    def test_delete_entry_view(self):
        entry = ActivityEntry.objects.filter(user=self.user).first()
        response = self.client.post(reverse('entry_delete', args=[entry.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ActivityEntry.objects.filter(user=self.user).count(), 0)

    def test_export_csv(self):
        response = self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_pdf(self):
        response = self.client.get(reverse('export_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_advice_api(self):
        response = self.client.get(reverse('get_advice'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('advice', data)
        self.assertIsInstance(data['advice'], list)
