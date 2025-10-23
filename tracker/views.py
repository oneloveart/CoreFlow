from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django import forms
from django.http import JsonResponse
from .models import ActivityEntry
from .utils import export_entries_csv, export_entries_pdf, generate_advice
import datetime
from .models import Message
from .utils import get_weather, get_urfu_news
from django.contrib.auth.models import User
import feedparser
from django.shortcuts import render
import os
from django.conf import settings

class EntryForm(forms.ModelForm):
    class Meta:
        model = ActivityEntry
        fields = ['category', 'start', 'end', 'note']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

def index(request):
    return render(request, 'tracker/index.html')

@login_required
def entry_list(request):
    entries = ActivityEntry.objects.filter(user=request.user).order_by('-start')
    return render(request, 'tracker/entry_list.html', {'entries': entries})

@login_required
def entry_detail(request, pk):
    entry = get_object_or_404(ActivityEntry, pk=pk, user=request.user)
    return render(request, 'tracker/entry_detail.html', {'entry': entry})

@login_required
def entry_add(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('entry_list')
    else:
        now = timezone.localtime()
        form = EntryForm(initial={'start': now, 'end': now})
    return render(request, 'tracker/entry_form.html', {'form': form})

@login_required
def entry_edit(request, pk):
    entry = get_object_or_404(ActivityEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('entry_list')
    else:
        form = EntryForm(instance=entry)
    return render(request, 'tracker/entry_form.html', {'form': form, 'edit': True})

@login_required
def entry_delete(request, pk):
    entry = get_object_or_404(ActivityEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('entry_list')
    return render(request, 'tracker/entry_confirm_delete.html', {'entry': entry})

# Export views
@login_required
def export_csv(request):
    return export_entries_csv(request.user)

@login_required
def export_pdf(request):
    return export_entries_pdf(request.user)

@login_required
def dashboard(request):
    today = timezone.localdate()
    start_dt = datetime.datetime.combine(today, datetime.time.min).astimezone(timezone.get_current_timezone())
    end_dt = datetime.datetime.combine(today, datetime.time.max).astimezone(timezone.get_current_timezone())
    qs = ActivityEntry.objects.filter(user=request.user, start__gte=start_dt, end__lte=end_dt)

    categories = ['study', 'rest', 'sleep', 'other']
    data = {cat: sum([e.duration_minutes for e in qs.filter(category=cat)]) for cat in categories}

    return render(request, 'tracker/dashboard.html', {'data': data})

# Advice view
@login_required
def get_advice(request):
    advice = generate_advice(request.user)
    return JsonResponse({'advice': advice})

# --- Погода ---
@login_required
def weather_view(request):
    weather = get_weather()
    return render(request, 'tracker/weather.html', {'weather': weather})

# --- Новости ---
def news_view(request):
    # Полный путь к локальному файлу urfu.xml
    local_rss_path = os.path.join(settings.BASE_DIR, 'urfu.xml')

    # Проверяем, существует ли файл
    if not os.path.exists(local_rss_path):
        return render(request, 'tracker/news.html', {'news_items': []})

    # Парсим RSS
    feed = feedparser.parse(f'file:///{local_rss_path}')

    news_items = []
    for entry in feed.entries:
        news_items.append({
            'title': entry.title.strip(),
            'link': entry.link.strip(),
            'pubDate': entry.get('published', '').strip(),
            'description': entry.get('description', '').strip(),
        })

    return render(request, 'tracker/news.html', {'news_items': news_items})
# --- Мессенджер ---
@login_required
def messages_view(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'tracker/messages.html', {'messages': messages, 'users': users})

@login_required
def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        text = request.POST.get('text')
        recipient = User.objects.get(id=recipient_id)
        Message.objects.create(sender=request.user, recipient=recipient, text=text)
    return redirect('messages')
