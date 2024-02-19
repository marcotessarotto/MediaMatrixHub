from django.contrib.auth import login
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SubscriberLoginForm, EventParticipationForm
from .models import Subscriber, InformationEvent, EventParticipation


def subscriber_login(request):
    if request.method == 'POST':
        form = SubscriberLoginForm(request.POST)
        if form.is_valid():
            matricola = form.cleaned_data['matricola']
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(matricola=matricola, email=email)

                # login(request, user, backend=AUTHENTICATION_BACKENDS[0])

                # Simulate login by saving subscriber's ID in session (example)
                request.session['subscriber_id'] = subscriber.id
                return redirect('manage-subscription')
            except Subscriber.DoesNotExist:
                messages.error(request, 'errore: matricola o email non validi')

    else:
        form = SubscriberLoginForm()
    return render(request, 'subscribers/login.html', {'form': form})


def manage_subscription(request):
    # check request.session['subscriber_id'] and retrieve the subscriber instance
    subscriber_id = request.session.get('subscriber_id')
    if subscriber_id:
        subscriber = Subscriber.objects.get(id=subscriber_id)
    else:
        raise Http404('Utente non trovato')

    if request.method == 'POST':
        form = EventParticipationForm(request.POST)
        if form.is_valid():
            # Assuming the user's subscriber information is available, e.g., through user profile
            subscriber = Subscriber.objects.get(email=request.user.email)
            for key, value in form.cleaned_data.items():
                if value:  # Checkbox is checked
                    event_id = key.split('_')[-1]
                    event = InformationEvent.objects.get(id=event_id)
                    EventParticipation.objects.create(event=event, subscriber=subscriber)
            return redirect('success_page')  # Redirect to a new URL
    else:
        form = EventParticipationForm()

    # return render(request, 'events/event_participation.html', {'form': form})

    return render(request, 'subscribers/manage_subscription.html', {'subscriber': subscriber, 'form': form})