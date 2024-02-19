from django.core.management.base import BaseCommand
from django.db.models import Count
from registration.models import InformationEvent


class Command(BaseCommand):
    help = 'Lists enabled events with their participation counts'

    def handle(self, *args, **options):
        # Fetch enabled events with participation count
        enabled_events_with_counts = InformationEvent.enabled_events.with_participation_count()

        if enabled_events_with_counts:
            self.stdout.write(self.style.SUCCESS('Enabled events with participation counts:'))
            for event in enabled_events_with_counts:
                self.stdout.write(f"{event.title}: {event.participation_count} participations")
        else:
            self.stdout.write(self.style.WARNING('No enabled events found.'))
