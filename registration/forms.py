from django import forms

from registration.models import InformationEvent


class SubscriberLoginForm(forms.Form):
    matricola = forms.CharField(label='Matricola', max_length=255)
    email = forms.EmailField(label='Email')


class EventParticipationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enabled_events = InformationEvent.objects.filter(enabled=True)
        for event in enabled_events:
            self.fields[f'event_{event.id}'] = forms.BooleanField(
                label=event.to_html_table(),
                required=False
            )
