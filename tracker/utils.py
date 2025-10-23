import csv
from io import BytesIO
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import ActivityEntry
import requests
from bs4 import BeautifulSoup
import feedparser

# --- PDF: регистрация шрифта с поддержкой кириллицы ---
# Замените путь на фактический путь к файлу DejaVuSans.ttf на вашем компьютере
pdfmetrics.registerFont(TTFont('DejaVuSans', r'C:\coreflow_project\templates\tracker\DejaVuSans.ttf'))

def export_entries_csv(user):
    # CSV с BOM для корректного отображения кириллицы в Excel
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="activities.csv"'
    response.write('\ufeff')  # BOM

    writer = csv.writer(response)
    writer.writerow(['Категория', 'Начало', 'Конец', 'Длительность (мин)', 'Заметка'])
    for entry in ActivityEntry.objects.filter(user=user).order_by('-start'):
        writer.writerow([
            entry.get_category_display(),
            entry.start.isoformat(),
            entry.end.isoformat(),
            entry.duration_minutes,
            entry.note
        ])
    return response

def export_entries_pdf(user):
    entries = ActivityEntry.objects.filter(user=user).order_by('-start')
    totals = {'study':0,'rest':0,'sleep':0,'other':0}
    for e in entries:
        totals[e.category] += e.duration_minutes

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activities_report.pdf"'
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Заголовок
    p.setFont('DejaVuSans', 16)
    p.drawString(50, height-50, 'TimeSaver — Отчёт по активностям')
    p.setFont('DejaVuSans', 12)
    p.drawString(50, height-80, f'Пользователь: {user.username}')
    p.drawString(50, height-100, f'Дата: {timezone.localtime().date().isoformat()}')

    # Totals с графиком
    y = height - 140
    p.setFont('DejaVuSans', 12)
    p.drawString(50, y, 'Итого (мин):')
    y -= 20
    max_total = max(totals.values()) if totals.values() else 1
    bar_max_width = 300
    for k,label in [('study','Учёба'),('rest','Отдых'),('sleep','Сон'),('other','Другое')]:
        val = totals.get(k,0)
        p.drawString(60, y, f'{label}: {val} мин')
        bar_w = int((val / (max_total if max_total>0 else 1)) * bar_max_width)
        p.setFillColorRGB(0.2,0.6,0.86)
        p.rect(200, y-4, bar_w, 10, fill=1)
        y -= 20
        if y < 120:
            p.showPage()
            y = height - 50

    # Список записей
    p.showPage()
    p.setFont('DejaVuSans', 14)
    p.drawString(50, height-50, 'Список записей')
    p.setFont('DejaVuSans', 10)
    y = height - 80
    for e in entries:
        line = f"{e.get_category_display()} | {e.start.strftime('%Y-%m-%d %H:%M')} - {e.end.strftime('%H:%M')} | {e.duration_minutes} мин | {e.note}"
        p.drawString(50, y, line[:130])
        y -= 14
        if y < 40:
            p.showPage()
            y = height - 40

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def generate_advice(user):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    entries = ActivityEntry.objects.filter(user=user, start__gte=week_ago)

    total = {'Учёба': 0, 'Отдых': 0, 'Сон': 0}
    for e in entries:
        category_label = e.get_category_display()
        if category_label in total:
            total[category_label] += (e.end - e.start).total_seconds() / 3600

    advice = []

    study = total['Учёба']
    rest = total['Отдых']
    sleep = total['Сон']

    if study < 10:
        advice.append("Ты учился меньше 10 часов за неделю. Попробуй поставить конкретные цели на день.")
    if rest > 15:
        advice.append("Отдых — это хорошо, но, возможно, ты отвлекаешься слишком часто. Попробуй метод Pomodoro.")
    if sleep < 40:
        advice.append("Ты спишь меньше 6 часов в сутки. Это может ухудшить концентрацию.")
    if 15 <= study <= 25 and 35 <= sleep <= 50 and rest <= 10:
        advice.append("Отличный баланс между учёбой, отдыхом и сном 💪 Продолжай в том же духе!")

    if not advice:
        advice.append("Данных пока недостаточно — добавь больше записей, чтобы получить рекомендации.")

    return advice

# --- Погода ---
def get_weather(city="Yekaterinburg"):
    api_key = "7549b3ff11a7b2f3cd25b56d21c83c6a"  # вставьте свой ключ
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={api_key}"
    data = requests.get(url).json()
    weather = {
        'city': city,
        'temp': data['main']['temp'],
        'description': data['weather'][0]['description'],
        'icon': data['weather'][0]['icon'],
    }
    return weather

# --- Новости URFU ---
def get_urfu_news():
    url = "https://urfu.ru/ru/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for item in soup.select('a.news-item-link')[:5]:  # последние 5 новостей
        title = item.get_text(strip=True)
        link = "https://urfu.ru" + item['href']
        news_items.append({'title': title, 'link': link})
    return news_items

URFU_NEWS_RSS = "https://urfu.ru/ru/news/rss/"

def get_urfu_news(limit=5):
    feed = feedparser.parse(URFU_NEWS_RSS)
    news_list = []
    for entry in feed.entries[:limit]:
        news_list.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published if 'published' in entry else '',
            'summary': entry.summary if 'summary' in entry else ''
        })
    return news_list