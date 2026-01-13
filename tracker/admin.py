from django.contrib import admin
from .models import ActivityEntry

@admin.register(ActivityEntry)
class ActivityEntryAdmin(admin.ModelAdmin):
    list_display = ('user','category','start','end','duration_minutes')
    list_filter = ('category', 'user')
