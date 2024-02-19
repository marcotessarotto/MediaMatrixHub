from django import forms
from django.utils import timezone

from registration.models import InformationEvent


class SubscriberLoginForm(forms.Form):
    matricola = forms.CharField(label='Matricola', max_length=255)
    email = forms.EmailField(label='Email')


class EventParticipationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_date = kwargs['current_date'] if 'current_date' in kwargs else timezone.now()

        # enabled_events = InformationEvent.objects.filter(enabled=True)
        enabled_events = InformationEvent.objects.filter(
            enabled=True,
            event_date__gte=current_date
        )

        for event in enabled_events:
            self.fields[f'event_{event.id}'] = forms.BooleanField(
                label=event.to_html_table(),
                required=False
            )
