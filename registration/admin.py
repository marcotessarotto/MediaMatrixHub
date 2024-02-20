from django.contrib import admin
from .models import InformationEvent, Subscriber, EventParticipation, EventLog


@admin.register(InformationEvent)
class InformationEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'event_date', 'event_start_time', 'enabled', 'created_at',)
    list_filter = ('enabled', 'event_date', 'speaker')
    search_fields = ('title', 'description', 'speaker', 'structure_name')
    date_hierarchy = 'event_date'
    ordering = ('-event_date', '-event_start_time')
    fields = (
    'title', 'speaker', 'event_date', 'event_start_time', 'meeting_url', 'structure_name', 'description', 'enabled')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'matricola')
    list_filter = ('name', 'surname')
    search_fields = ('email', 'name', 'surname', 'matricola')


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'subscriber', 'created_at', )
    list_filter = ('event', 'subscriber')
    search_fields = ('event__title', 'subscriber__name', 'subscriber__surname')


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'event_type', 'event_title', 'event_target', 'event_data', 'created_at')
    list_filter = [ 'event_type']


