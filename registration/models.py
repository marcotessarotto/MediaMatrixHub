import uuid
import datetime

import pytz
from django.db import models
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.html import format_html
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from mediamatrixhub.settings import PRODID, INTERNET_DOMAIN, BASE_URL


class InformationEventQuerySet(models.QuerySet):
    def with_participation_count(self):
        return self.annotate(participation_count=Count('eventparticipation'))


class EnabledEventManager(models.Manager):
    def get_queryset(self):
        return InformationEventQuerySet(self.model, using=self._db).filter(enabled=True).order_by('-event_date',
                                                                                                  '-event_start_time')

    def with_participation_count(self):
        # Ensure it operates on the current queryset
        return self.get_queryset().annotate(participation_count=Count('eventparticipation'))


class InformationEvent(models.Model):
    """
    Model for InformationEvent, representing an event that users can participate in.

    Attributes:
        event_date (Date): The date of the event.
        event_start_time (Time): The start time of the event.
        meeting_url (URL): The URL for participating in the event.
        speaker (str): The speaker of the event.
        structure_name (str, optional): The name of the structure associated with the event.
        structure_matricola (str, optional): The matricola of the structure associated with the event.
        title (str): The title of the event.
        description (str, optional): The description of the event.
        enabled (bool): Indicates if the event is enabled.

    Methods:
        to_html_table_email(): Returns a Bootstrap-styled HTML table representation of the InformationEvent instance for email templates.
        to_html_table(): Returns a Bootstrap-styled HTML table representation of the InformationEvent instance for web pages.
    """
    objects = models.Manager()  # The default manager.
    enabled_events = EnabledEventManager()  # Custom manager for enabled events.

    EVENT_TYPE_CHOICES = [
        ('virtual', _("Virtuale")),
        ('physical', _("Fisico")),
        ('hybrid', _("Ibrido"))
    ]
    event_type = models.CharField(max_length=8, choices=EVENT_TYPE_CHOICES, default='virtual', verbose_name=_("Tipo di evento"))
    event_date = models.DateField(verbose_name=_("data evento"))
    event_start_time = models.TimeField(verbose_name=_("ora inizio"))
    event_end_time = models.TimeField(verbose_name=_("ora fine"), blank=True, null=True)
    meeting_url = models.URLField(verbose_name=_("URL per partecipare"), max_length=255)
    speaker = models.CharField(verbose_name=_("Speaker"), max_length=255)
    structure_name = models.CharField(verbose_name=_("Nome struttura"), max_length=255, blank=True)
    structure_matricola = models.CharField(verbose_name=_("Matricola struttura"), max_length=255, blank=True)
    title = models.CharField(verbose_name=_("Titolo evento"), max_length=255)
    description = models.TextField(verbose_name=_("Descrizione"), blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)
    category = models.ForeignKey("core.Category", on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_("Categoria"))
    location = models.CharField(max_length=255, verbose_name=_("Località"), blank=True, null=True,
                                help_text=_("Required for physical and hybrid events."))
    max_participants = models.IntegerField(verbose_name=_("Numero massimo partecipanti"), null=True, blank=True)
    registration_deadline = models.DateField(verbose_name=_("Termine iscrizione"), null=True, blank=True)
    STATUS_CHOICES = [
        ('planned', _("Planned")),
        ('ongoing', _("Ongoing")),
        ('completed', _("Completed")),
        ('cancelled', _("Cancelled")),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned', verbose_name=_("Stato evento"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Cancellato"))
    image = models.ImageField(upload_to='information_event_images/', blank=True, null=True, verbose_name=_("Immagine evento"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_("Meta Description"))
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Keywords"))

    ref_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Information Event")
        verbose_name_plural = _("Information Events")

    def to_html_table_email(self):
        """
                Returns a Bootstrap-styled HTML table representation of the InformationEvent instance.
                For use in email templates.

                Returns:
                    str: The HTML table representation of the InformationEvent instance.

                Examples:
                    >>> event = InformationEvent.objects.get(pk=1)
                    >>> html_table = event.to_html_table_email()
                    >>> print(html_table)
                    <table>...</table>
        """
        # Format date as 'mercoledì 28 febbraio 2024'
        formatted_event_date = formats.date_format(self.event_date, "l j F Y") if self.event_date else "N/A"

        context = {
            'event': self,
            'BASE_URL': BASE_URL,
            'event_date': formatted_event_date,
        }
        return render_to_string('fragment/information_event_email.html', context)

    def to_html_table(self):
        """
                Returns a Bootstrap-styled HTML table representation of the InformationEvent instance
                to be used in web pages.

                Returns:
                    str: The HTML table representation of the InformationEvent instance.

                Examples:
                    >>> event = InformationEvent.objects.get(pk=1)
                    >>> html_table = event.to_html_table()
                    >>> print(html_table)
                    <table>...</table>
        """
        # formatted_event_date = date_format(self.event_date, "d/m/Y")  # Format date to Italian format DD/MM/YYYY

        # Format date as 'mercoledì 28 febbraio 2024'
        formatted_event_date = formats.date_format(self.event_date, "l j F Y") if self.event_date else "N/A"

        context = {
            'event': self,
            'event_date': formatted_event_date,
        }
        html_content = render_to_string('fragment/information_event_table.html', context)
        return format_html(html_content)

    def generate_ics_content(self):
        """
        Generates the content of an .ics file for importing the event into calendar applications.

        Returns:
            str: The .ics file content as a string.
        """
        # Format start and end times into the required format
        if self.event_date and self.event_start_time:
            # Combine date and time for start
            dt_start = datetime.datetime.combine(self.event_date, self.event_start_time)
            # Assuming event_end_time is available and combining it with event_date
            if self.event_end_time:
                dt_end = datetime.datetime.combine(self.event_date, self.event_end_time)
            else:
                # Assuming a default duration of 1 hour if end time is not provided
                dt_end = dt_start + datetime.timedelta(hours=1)
        else:
            # Return an empty string or handle the case where date/time is not available
            return ""

        # Convert to UTC
        dt_start_utc = dt_start.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
        dt_end_utc = dt_end.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')

        # Generate UID based on event details to ensure uniqueness
        uid = f"{self.ref_token}@{INTERNET_DOMAIN}"
        
        ics_description = self.description.replace("\n", "\\n")

        # Prepare .ics content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-{PRODID}
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{timezone.now().astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dt_start_utc}
DTEND:{dt_end_utc}
SUMMARY:{self.title}
DESCRIPTION:{ics_description}
LOCATION:{self.location or "N/A"}
URL:{self.meeting_url}
END:VEVENT
END:VCALENDAR
"""
        return ics_content


class Subscriber(models.Model):
    """
    Model for Subscriber, representing a subscriber with email, name, surname, and matricola.

    Attributes:
        email (str): The email of the subscriber.
        name (str): The name of the subscriber.
        surname (str): The surname of the subscriber.
        matricola (str): The matricola of the subscriber.

    Methods:
        __str__(): Returns a string representation of the Subscriber instance.
    """
    email = models.EmailField(verbose_name=_("Email"), max_length=255)
    name = models.CharField(verbose_name=_("Nome"), max_length=255)
    surname = models.CharField(verbose_name=_("Cognome"), max_length=255)
    matricola = models.CharField(verbose_name=_("Matricola"), max_length=255)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")


class EventParticipation(models.Model):
    """
    Model for EventParticipation, representing the participation of a subscriber in an event.

    Attributes:
        event (InformationEvent): The event in which the subscriber participates.
        subscriber (Subscriber): The subscriber participating in the event.

    Methods:
        __str__(): Returns a string representation of the EventParticipation instance.
    """
    event = models.ForeignKey(InformationEvent, on_delete=models.CASCADE, verbose_name=_("Evento"))
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, verbose_name=_("Subscriber"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event} {self.subscriber}"

    class Meta:
        verbose_name = _("Event Participation")
        verbose_name_plural = _("Event Participations")


class EventLog(models.Model):
    """
    Represents an event log entry.

    Args:
        event_type (str): The type of the event.
        event_title (str): The title of the event.
        event_data (str): The data associated with the event.
        event_target (str, optional): The target of the event.

    Returns:
        str: A string representation of the EventLog.

    Examples:
        >>> event = EventLog(event_type="LOGIN", event_title="User Login", event_data="User 'john' logged in successfully")
        >>> print(event)
        EventLog #1  event_type=LOGIN event_target=None event_title=User Login 2022-01-01 12:00:00
    """
    ERROR_SENDING_EMAIL = "ERROR_SENDING_EMAIL"
    EMAIL_SENT = "EMAIL_SENT"
    SUBSCRIPTION_SET = "SUBSCRIPTION_SET"
    SUBSCRIPTION_REMOVED = "SUBSCRIPTION_REMOVED"
    LOGIN = "LOGIN"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    REMAINDER_EMAIL_SENT = "REMAINDER_EMAIL_SENT"

    created_at = models.DateTimeField(auto_now_add=True)

    event_type = models.CharField(max_length=128, null=True)
    event_title = models.CharField(max_length=256, null=True)
    event_data = models.TextField(null=True)
    event_target = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"EventLog #{self.id}  event_type={self.event_type} event_target={self.event_target} event_title={self.event_title} {self.created_at}"


