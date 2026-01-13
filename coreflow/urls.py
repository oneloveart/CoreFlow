from django.contrib import admin
from django.urls import path, include
from tracker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include('tracker.api_urls')),  # если используешь API
    path('', views.index, name='index'),
    path('entries/', include('tracker.urls')),  # CRUD, экспорт и старые маршруты
    path('dashboard/', views.dashboard, name='dashboard'),

    # Новые маршруты напрямую
    path('weather/', views.weather_view, name='weather'),
    path('news/', views.news_view, name='news'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/send/', views.send_message, name='send_message'),
]