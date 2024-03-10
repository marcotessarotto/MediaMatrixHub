from django import forms
from django.utils import timezone

from registration.models import InformationEvent


class SubscriberLoginForm(forms.Form):
    # matricola = forms.CharField(label='Matricola', max_length=255)
    # email = forms.EmailField(label='Email regionale')

    matricola = forms.CharField(
        label='Matricola',
        max_length=255,
        widget=forms.TextInput(attrs={'size': '40'})  # Specify size for matricola field
    )

    email = forms.EmailField(
        label='Email regionale',
        widget=forms.EmailInput(attrs={'size': '40'})  # Here we specify the size
    )


class EventParticipationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Pop 'current_date' from kwargs if it exists, otherwise use the current date
        current_date = kwargs.pop('current_date', timezone.now().date())

        super().__init__(*args, **kwargs)

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

        self.number_of_events = len(enabled_events)