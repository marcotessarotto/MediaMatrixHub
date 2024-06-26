from datetime import timedelta

from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone, formats

from mediamatrixhub.email_utils import my_send_email
from mediamatrixhub.settings import REGISTRATION_URL, SUBJECT_EMAIL, DEBUG_EMAIL, TECHNICAL_CONTACT_EMAIL, \
    TECHNICAL_CONTACT, VIDEOTECA_URL, FROM_EMAIL, EMAIL_HOST
from registration.logic import create_event_log
from registration.models import InformationEvent, Subscriber, EventLog


class Command(BaseCommand):
    help = 'Send remainder email to subscribers for tomorrow events.'

    # parse parameters
    def add_arguments(self, parser):
        parser.add_argument('--debug', action='store_true', help='Debug mode')
        # add optional argument 'days' to specify the number of days to look ahead
        parser.add_argument('--days', type=int, help='Number of days to look ahead')

    def handle(self, *args, **options):
        debug_mode = options['debug']

        number_of_days = 1
        days = options['days']

        if days is not None and days >= 0:
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

            counter = 0

            # self.stdout.write(self.style.SUCCESS('Subscribers for this event:'))
            for subscriber in subscribers_for_event:
                self.stdout.write(f"Subscriber: {subscriber.name} {subscriber.surname}, {subscriber.email}")

                context = {
                    'subscriber': subscriber,
                    'event': event,
                    'event_html_table': event.to_html_table_email(),
                    'APPLICATION_TITLE': 'Media Matrix Hub',
                    'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
                    'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
                    'REGISTRATION_URL': REGISTRATION_URL,
                    'VIDEOTECA_URL': VIDEOTECA_URL,
                    'tomorrow_str': tomorrow_str,
                }

                message_body = render_to_string('fragment/information_event_send_remainder_it.html', context)

                message_subject = f'{SUBJECT_EMAIL} Promemoria per la prossima pillola informativa'

                if not debug_mode:
                    try:

                        my_send_email(
                            FROM_EMAIL,
                            [subscriber.email],
                            message_subject,
                            message_body,
                            bcc_addresses=None,
                            attachments=None,
                            email_host=EMAIL_HOST
                        )

                        create_event_log(
                            event_type=EventLog.REMAINDER_EMAIL_SENT,
                            event_title=message_subject,
                            event_data=f"subscriber: {subscriber} email: {subscriber.email} {message_body}",
                            event_target=subscriber.email,
                        )
                        self.stdout.write(self.style.SUCCESS(f"Email sent to {subscriber.email}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error sending email to {subscriber.email}: {e}"))

                        create_event_log(EventLog.ERROR_SENDING_EMAIL,
                                         f"Error sending email to {subscriber.email}",
                                         f"Error sending email to {subscriber.email}: {e}",
                                         subscriber.email)
                else:
                    self.stdout.write(f"debug mode: fake sending email to {subscriber.email}")
                    self.stdout.write(f"message: {message_body}  (debug mode)")

                counter += 1

            self.stdout.write(self.style.SUCCESS(f"Email sent to {counter} subscribers for event {event.title}"))

            message_subject = f'{SUBJECT_EMAIL} Resoconto invio email promemoria per la prossima pillola informativa'
            message_body = f'Promemoria inviato a {counter} iscritti per l\'evento {event.title} del {tomorrow_str}.'

            my_send_email(
                FROM_EMAIL,
                [DEBUG_EMAIL],
                message_subject,
                message_body,
                bcc_addresses=None,
                attachments=None,
                email_host=EMAIL_HOST
            )

        self.stdout.write(self.style.SUCCESS('Done.'))
