from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone, formats

from mediamatrixhub.email_utils import send_simple_html_email
from mediamatrixhub.settings import REGISTRATION_URL, SUBJECT_EMAIL, DEBUG_EMAIL
from registration.logic import create_event_log
from registration.models import InformationEvent, Subscriber, EventLog


class Command(BaseCommand):
    help = 'Lists enabled events with their participation counts'

    # parse parameters
    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='Debug mode')
        # add optional argument 'days' to specify the number of days to look ahead
        parser.add_argument('--days', type=int, help='Number of days to look ahead')

    def handle(self, *args, **options):
        debug_mode = options['debug']

        number_of_days = 1
        days = options['days']
        if days and days >= 0:
            self.stdout.write(self.style.SUCCESS(f'Looking ahead {days} days'))
            number_of_days = days
        else:
            self.stdout.write(self.style.WARNING(f'Looking ahead {number_of_days} day'))

        if debug_mode:
            self.stdout.write(self.style.SUCCESS('Debug mode enabled'))
        else:
            self.stdout.write(self.style.WARNING('Debug mode disabled'))

        # Calculate tomorrow's date
        tomorrow = timezone.now().date() + timedelta(days=number_of_days)
        # format tomorrow a string in extended italian format
        # tomorrow_str = tomorrow.strftime("%A %d %B %Y")
        tomorrow_str = formats.date_format(tomorrow, "l j F Y")

        # Query EnabledEventManager instances where event_date is tomorrow
        tomorrow_events = InformationEvent.enabled_events.filter(event_date=tomorrow).with_participation_count()

        if not tomorrow_events:
            self.stdout.write(self.style.WARNING(f'No enabled events found for {tomorrow_str}.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Enabled events for {tomorrow_str}:'))

        event: InformationEvent

        for event in tomorrow_events:
            self.stdout.write(f"#{event.id}, {event.title}, {event.event_date}: {event.participation_count} iscrizioni")

            # Assuming 'event' is your InformationEvent instance
            subscribers_for_event = Subscriber.objects.filter(eventparticipation__event=event)

            if not subscribers_for_event:
                self.stdout.write(self.style.WARNING('No subscribers found for this event.'))
                continue

            # self.stdout.write(self.style.SUCCESS('Subscribers for this event:'))
            for subscriber in subscribers_for_event:
                self.stdout.write(f"Subscriber: {subscriber.name} {subscriber.surname}, {subscriber.email}")

                # send email to subscriber
                message_body = f'Ciao {subscriber.surname},<br><br>' \
                               f'Ti ricordiamo che il prossimo evento informativo si terrà il giorno {tomorrow_str}.<br><br>' \
                               f"Ecco un riepilogo dell'evento a cui ti sei iscritto:<br><br>" \
                               f'{event.to_html_table_email()}<br><br>' \    
                               f'Grazie per la tua partecipazione.<br><br><br>' \
                               f'Se vuoi modificare le tue iscrizioni alle pillole informative, vai a questo link: ' \
                               f'<a href="{REGISTRATION_URL}">{REGISTRATION_URL}</a><br><br>'

                message_subject = f'{SUBJECT_EMAIL} Promemoria per la prossima pillola informativa'

                if not debug_mode:
                    send_simple_html_email(
                        list_of_email_addresses=[subscriber.email],
                        subject=message_subject,
                        message_body=message_body,
                        list_of_bcc_email_addresses=[DEBUG_EMAIL],
                    )

                    create_event_log(
                        event_type=EventLog.REMAINDER_EMAIL_SENT,
                        event_title=message_subject,
                        event_data=f"subscriber: {subscriber} email: {subscriber.email} {message_body}",
                        event_target=subscriber.email,
                    )
                    self.stdout.write(self.style.SUCCESS(f"Email sent to {subscriber.email}"))
                else:
                    self.stdout.write(f"debug mode: fake sending email to {subscriber.email}")
                    self.stdout.write(f"message: {message_body}  (debug mode)")

        self.stdout.write(self.style.SUCCESS('Done.'))
