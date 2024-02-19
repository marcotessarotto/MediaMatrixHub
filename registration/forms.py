
from django import forms

class SubscriberLoginForm(forms.Form):
    matricola = forms.CharField(label='Matricola', max_length=255)
    email = forms.EmailField(label='Email')
