from django.db import models

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
        return f"{self.person_name} {self.person_surname}"

    class Meta:
        verbose_name = _("Event Participation")
        verbose_name_plural = _("Event Participations")
