from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import formats

from registration.models import InformationEvent


class Command(BaseCommand):
    help = 'Lists enabled events with their participation counts'

    def handle(self, *args, **options):
        # Fetch enabled events with participation count
        enabled_events_with_counts = InformationEvent.enabled_events.with_participation_count().order_by(
            'event_date', 'event_start_time')

        if enabled_events_with_counts:
            self.stdout.write(self.style.SUCCESS('Enabled events with participation counts:'))
            for event in enabled_events_with_counts:
                formatted_event_date = formats.date_format(event.event_date, "l j F Y") if event.event_date else "N/A"

                self.stdout.write(f"#{event.id}, {event.title}, {formatted_event_date}: {event.participation_count} iscrizioni")
        else:
            self.stdout.write(self.style.WARNING('No enabled events found.'))
