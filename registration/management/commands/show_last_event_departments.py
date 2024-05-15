import json
import os

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import formats, timezone

from mediamatrixhub.email_utils import my_send_email
from mediamatrixhub.settings import SUBJECT_EMAIL, MONITOR_EMAIL_ADDRESSES, FROM_EMAIL, EMAIL_HOST
from registration.models import InformationEvent


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def lookup_email(data, email):
    for person, details in data.items():
        if details[1] == email:
            return details[6]
    return None


class Command(BaseCommand):
    help = 'show departments of the last event'

    # parse parameters
    def add_arguments(self, parser):
        parser.add_argument('--send_email', action='store_true', help='Send email to subscribers')

    def handle(self, *args, **options):
        send_email = options['send_email']

        # fetch the last event
        last_event = InformationEvent.enabled_events.first()

        if not last_event:
            self.stdout.write(self.style.WARNING('No enabled events found.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Departments of the last event "{last_event.title}":'))

        # fetch all EventParticipation objects for the last event
        event_participations = last_event.eventparticipation_set.all()

        # print current working directory
        print(os.getcwd())

        json_data = read_json_file('registration/res/persfvg_dump_persone_entita.json')

        dict_department = {}

        email_body = ""

        email_body += f"<h1>Strutture di appartenenza degli iscritti alla pillola #{last_event.id} {last_event.title }</h1><br><br>"

        for event_participation in event_participations:
            email = event_participation.subscriber.email
            department = lookup_email(json_data, email)
            # self.stdout.write(f"{email}: {department}")

            if department in dict_department:
                dict_department[department] += 1
            else:
                dict_department[department] = 1

        # sort dict_department by key
        dict_department = dict(sorted(dict_department.items(), key=lambda item: item[0]))

        # print dict_department
        for key, value in dict_department.items():
            self.stdout.write(f"{key}: {value}")
            email_body += f"{key}: {value}<br>"

        current_date = timezone.now().date()
        # add today date to email_body
        email_body += f"<br><br><p>Report generato il {formats.date_format(current_date, 'l j F Y')}.</p>"

        # Specify email details
        list_of_email_addresses = MONITOR_EMAIL_ADDRESSES  # Add actual recipient email address
        subject = f'{SUBJECT_EMAIL} Strutture di appartenenza degli iscritti alla pillola #{last_event.id} {last_event.title }'

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
