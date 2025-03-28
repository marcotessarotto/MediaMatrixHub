from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import formats, timezone

from core.logic import get_video_playback_events_totals
from mediamatrixhub.email_utils import my_send_email
from mediamatrixhub.settings import SUBJECT_EMAIL, MONITOR_EMAIL_ADDRESSES, FROM_EMAIL, EMAIL_HOST
from registration.models import InformationEvent


class Command(BaseCommand):
    help = 'Lists enabled events with their participation counts'

    # parse parameters
    def add_arguments(self, parser):
        parser.add_argument('--send_email', action='store_true', help='Send email to subscribers')

    def handle(self, *args, **options):
        send_email = options['send_email']

        # Fetch enabled events with participation count
        enabled_events_with_counts = InformationEvent.enabled_events.with_participation_count().order_by(
            'event_date', 'event_start_time')

        video_playback_events_totals = get_video_playback_events_totals()

        if not send_email:

            if enabled_events_with_counts:
                self.stdout.write(self.style.SUCCESS('Enabled events with participation counts:'))
                for event in enabled_events_with_counts:
                    formatted_event_date = formats.date_format(event.event_date, "l j F Y") if event.event_date else "N/A"

                    self.stdout.write(f"#{event.id}, {event.title}, {formatted_event_date}: {event.participation_count} iscrizioni")
            else:
                self.stdout.write(self.style.WARNING('No enabled events found.'))
        else:

            # Start constructing the email body
            email_body = ""
            if enabled_events_with_counts:
                self.stdout.write(self.style.SUCCESS('Enabled events with participation counts:'))
                email_body += "<h1>Pillole informative con conteggio iscritti</h1><br><br>"
                for event in enabled_events_with_counts:
                    formatted_event_date = formats.date_format(event.event_date,
                                                               "l j F Y") if event.event_date else "N/A"
                    event_info = f"#{event.id}, {event.title}, {formatted_event_date}: {event.participation_count} iscrizioni<br>"
                    self.stdout.write(event_info)
                    email_body += event_info

                email_body += "<br><br>"

                # add video_playback_events_totals to email_body
                email_body += "<h1>Conteggio visualizzazioni pillole informative</h1><br>"
                email_body += "<p>Conteggio delle visualizzazioni delle pillole informative da parte di utenti unici</p><br>"
                for video_title, count in video_playback_events_totals.items():
                    video_info = f"{video_title}: {count} visualizzazioni<br>"
                    self.stdout.write(video_info)
                    email_body += video_info

                email_body += "<br><br>"

                current_date = timezone.now().date()
                # add today date to email_body
                email_body += f"<br><br><p>Report generato il {formats.date_format(current_date, 'l j F Y')}.</p>"
            else:
                message = 'Non ci sono pillole informative programmate in futuro, al momento.'
                self.stdout.write(self.style.WARNING(message))
                email_body += f"<p>{message}</p>"

                return

            # Specify email details
            list_of_email_addresses = MONITOR_EMAIL_ADDRESSES  # Add actual recipient email address
            subject = f'{SUBJECT_EMAIL} Monitoraggio iscrizioni a pillole informative'

            my_send_email(
                FROM_EMAIL,
                list_of_email_addresses,
                subject,
                email_body,
                bcc_addresses=None,
                attachments=None,
                email_host=EMAIL_HOST
            )

            self.stdout.write(self.style.SUCCESS('Email sent successfully.'))
