from django.db import models
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import formats
from django.utils.formats import date_format
from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _


class EnabledEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True).order_by('-event_date', '-event_start_time')

    def with_participation_count(self):
        # Ensure it operates on the current queryset
        return self.get_queryset().annotate(participation_count=Count('eventparticipation'))


class InformationEvent(models.Model):
    """
    Model for InformationEvent, which represents an event that users can participate in.
    """
    objects = models.Manager()  # The default manager.
    enabled_events = EnabledEventManager()  # Custom manager for enabled events.

    event_date = models.DateField(verbose_name=_("data evento"))
    event_start_time = models.TimeField(verbose_name=_("ora inizio"))
    meeting_url = models.URLField(verbose_name=_("URL per partecipare"), max_length=255)
    speaker = models.CharField(verbose_name=_("Speaker"), max_length=255)
    structure_name = models.CharField(verbose_name=_("Nome struttura"), max_length=255, blank=True)
    structure_matricola = models.CharField(verbose_name=_("Matricola struttura"), max_length=255, blank=True)
    title = models.CharField(verbose_name=_("Titolo evento"), max_length=255)
    description = models.TextField(verbose_name=_("Descrizione"), blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Information Event")
        verbose_name_plural = _("Information Events")

    def to_html_table_email(self):
        """
        Returns a Bootstrap-styled HTML table representation of the InformationEvent instance.
        For use in email templates.
        """
        # Format date as 'mercoledì 28 febbraio 2024'
        formatted_event_date = formats.date_format(self.event_date, "l j F Y") if self.event_date else "N/A"

        context = {
            'event': self,
            'event_date': formatted_event_date,
        }
        return render_to_string('fragment/information_event_email.html', context)

        # return format_html(
        #     '''
        #     <table class="table">
        #         <tbody>
        #             <tr><td width="200px">Titolo Evento</td><td>{title}</td></tr>
        #             <tr><td>Descrizione</td><td>{description}</td></tr>
        #             <tr><td>Data Evento</td><td>{event_date} {event_start_time}</td></tr>
        #             <tr><td>URL per Partecipare</td><td><a href="{meeting_url}">{meeting_url}</a></td></tr>
        #             <tr><td>Speaker</td><td>{speaker}</td></tr>
        #             <tr><td>Nome Struttura</td><td>{structure_name}</td></tr>
        #         </tbody>
        #     </table>
        #     ''',
        #     event_date=formatted_event_date,
        #     event_start_time=self.event_start_time,
        #     meeting_url=self.meeting_url,
        #     speaker=self.speaker,
        #     structure_name=self.structure_name or 'N/A',  # Handle blank fields
        #     structure_matricola=self.structure_matricola or 'N/A',
        #     title=self.title,
        #     description=self.description or 'N/A',
        #     enabled="Yes" if self.enabled else "No",
        # )

    def to_html_table(self):
        """
        Returns a Bootstrap-styled HTML table representation of the InformationEvent instance
        to be used in web pages.
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

        # return format_html(
        #     '''
        #     <table class="table uniform-table">
        #         <!--<thead>
        #             <tr>
        #                 <th scope="col">Field</th>
        #                 <th scope="col">Value</th>
        #             </tr>
        #         </thead>-->
        #         <tbody>
        #             <tr><td width="200px">Titolo Evento</td><td>{title}</td></tr>
        #             <tr><td>Descrizione</td><td>{description}</td></tr>
        #             <tr><td>Data Evento</td><td>{event_date} {event_start_time}</td></tr>
        #             <!--<tr><td>Ora Inizio</td><td>{event_start_time}</td></tr>-->
        #             <!-- <tr><td>URL per Partecipare</td><td><a href="{meeting_url}">{meeting_url}</a></td></tr>-->
        #             <tr><td>Speaker</td><td>{speaker}</td></tr>
        #             <tr><td>Nome Struttura</td><td>{structure_name}</td></tr>
        #         </tbody>
        #     </table>
        #     ''',
        #     event_date=formatted_event_date,
        #     event_start_time=self.event_start_time,
        #     meeting_url=self.meeting_url,
        #     speaker=self.speaker,
        #     structure_name=self.structure_name or 'N/A',  # Handle blank fields
        #     structure_matricola=self.structure_matricola or 'N/A',
        #     title=self.title,
        #     description=self.description or 'N/A',
        #     enabled="Yes" if self.enabled else "No",
        # )


class Subscriber(models.Model):
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
