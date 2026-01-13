from django.urls import path
from . import views

urlpatterns = [
    # CRUD записи активности
    path('', views.entry_list, name='entry_list'),
    path('add/', views.entry_add, name='entry_add'),
    path('<int:pk>/edit/', views.entry_edit, name='entry_edit'),
    path('<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('<int:pk>/', views.entry_detail, name='entry_detail'),

    # Экспорт
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),

    # Советы
    path('advice/', views.get_advice, name='get_advice'),

    # Новые функции
    path('weather/', views.weather_view, name='weather'),
    path('news/', views.news_view, name='news'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/send/', views.send_message, name='send_message'),

    path("messages/", views.messages_view, name="messages"),
    path("messages/send/", views.send_message, name="send_message"),
    path("messages/history/", views.messages_history_api, name="messages_history_api"),

]
