from django.db import models
from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _


class EnabledEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True).order_by('-event_date', '-event_start_time')


class InformationEvent(models.Model):
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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Information Event")
        verbose_name_plural = _("Information Events")

    def to_html_table_email(self):
        """
        Returns a Bootstrap-styled HTML table representation of the InformationEvent instance
        without row IDs.
        """
        html = format_html(
            '''
            <table class="table">
                <tbody>
                    <tr><td width="200px">Titolo Evento</td><td>{title}</td></tr>            
                    <tr><td>Descrizione</td><td>{description}</td></tr>                        
                    <tr><td>Data Evento</td><td>{event_date} </td></tr>
                    <tr><td>URL per Partecipare</td><td><a href="{meeting_url}">{meeting_url}</a></td></tr>
                    <tr><td>Speaker</td><td>{speaker}</td></tr>
                    <tr><td>Nome Struttura</td><td>{structure_name}</td></tr>
                </tbody>
            </table>
            ''',
            event_date=self.event_date,
            event_start_time=self.event_start_time,
            meeting_url=self.meeting_url,
            speaker=self.speaker,
            structure_name=self.structure_name or 'N/A',  # Handle blank fields
            structure_matricola=self.structure_matricola or 'N/A',
            title=self.title,
            description=self.description or 'N/A',
            enabled="Yes" if self.enabled else "No",
        )
        return html


    def to_html_table(self):
        """
        Returns a Bootstrap-styled HTML table representation of the InformationEvent instance
        without row IDs.
        """
        html = format_html(
            '''
            <table class="table uniform-table">
                <!--<thead>
                    <tr>
                        <th scope="col">Field</th>
                        <th scope="col">Value</th>
                    </tr>
                </thead>-->
                <tbody>
                    <tr><td width="200px">Titolo Evento</td><td>{title}</td></tr>            
                    <tr><td>Descrizione</td><td>{description}</td></tr>                        
                    <tr><td>Data Evento</td><td>{event_date} </td></tr>
                    <!--<tr><td>Ora Inizio</td><td>{event_start_time}</td></tr>-->
                    <!-- <tr><td>URL per Partecipare</td><td><a href="{meeting_url}">{meeting_url}</a></td></tr>-->
                    <tr><td>Speaker</td><td>{speaker}</td></tr>
                    <tr><td>Nome Struttura</td><td>{structure_name}</td></tr>
                </tbody>
            </table>
            ''',
            event_date=self.event_date,
            event_start_time=self.event_start_time,
            meeting_url=self.meeting_url,
            speaker=self.speaker,
            structure_name=self.structure_name or 'N/A',  # Handle blank fields
            structure_matricola=self.structure_matricola or 'N/A',
            title=self.title,
            description=self.description or 'N/A',
            enabled="Yes" if self.enabled else "No",
        )
        return html


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

    def __str__(self):
        return f"{self.event} {self.subscriber}"

    class Meta:
        verbose_name = _("Event Participation")
        verbose_name_plural = _("Event Participations")
