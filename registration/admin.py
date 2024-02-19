from django.contrib import admin
from .models import InformationEvent


@admin.register(InformationEvent)
class InformationEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'event_date', 'event_start_time', 'enabled')
    list_filter = ('enabled', 'event_date', 'speaker')
    search_fields = ('title', 'description', 'speaker', 'structure_name')
    date_hierarchy = 'event_date'
    ordering = ('-event_date', '-event_start_time')
    fields = (
    'title', 'speaker', 'event_date', 'event_start_time', 'meeting_url', 'structure_name', 'description', 'enabled')
