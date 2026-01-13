from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class ActivityEntry(models.Model):
    CATEGORY_CHOICES = [
        ('study','Учёба'),
        ('rest','Отдых'),
        ('sleep','Сон'),
        ('other','Другое'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    start = models.DateTimeField()
    end = models.DateTimeField()
    note = models.TextField(blank=True)

    @property
    def duration_minutes(self):
        delta = self.end - self.start
        return int(delta.total_seconds() // 60)

    def save(self, *args, **kwargs):
        if self.end < self.start:
            self.start, self.end = self.end, self.start
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.get_category_display()} ({self.start.date()})"

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.text[:20]}"