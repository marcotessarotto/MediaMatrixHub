import syslog

from django.contrib.auth import login
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from mediamatrixhub.email_utils import send_simple_html_email
from mediamatrixhub.settings import DEBUG, DEBUG_EMAIL
from mediamatrixhub.view_tools import is_private_ip
from .forms import SubscriberLoginForm, EventParticipationForm
from .models import Subscriber, InformationEvent, EventParticipation


def subscriber_login(request):
    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')
    # print(http_real_ip)

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
        return HttpResponse(status=403)

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
    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')
    # print(http_real_ip)

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        return HttpResponse(status=403)

    # check request.session['subscriber_id'] and retrieve the subscriber instance
    subscriber_id = request.session.get('subscriber_id')
    if subscriber_id:
        subscriber = Subscriber.objects.get(id=subscriber_id)
    else:
        raise Http404('Utente non trovato')

    if request.method == 'POST':
        form = EventParticipationForm(request.POST)
        if form.is_valid():
            subscriptions = []

            for key, value in form.cleaned_data.items():
                if value:  # Checkbox is checked
                    event_id = key.split('_')[-1]
                    event = InformationEvent.objects.get(id=event_id)
                    # Check if the EventParticipation instance exists and update or create accordingly
                    EventParticipation.objects.update_or_create(
                        event=event, subscriber=subscriber,
                        defaults={'event': event, 'subscriber': subscriber}
                    )

                    subscriptions.append(event.to_html_table_email())
                else:
                    # If the checkbox is not checked, delete the EventParticipation instance
                    event_id = key.split('_')[-1]
                    event = InformationEvent.objects.get(id=event_id)
                    EventParticipation.objects.filter(event=event, subscriber=subscriber).delete()

            messages.success(request,
                             'Iscrizioni alle pillole informative aggiornate con successo. Ti ho inviato una email riassuntiva con i dettagli per accedere.')

            # invia email riassuntiva all'utente
            if subscriptions:
                send_simple_html_email(
                    list_of_email_addresses=[subscriber.email],
                    subject='Riepilogo iscrizioni pillole informative',
                    message_body=f'Ciao {subscriber.surname},<br><br>' \
                                 f'hai aggiornato con successo le tue iscrizioni alle pillole informative.<br><br>' \
                                 f'Ecco un riepilogo delle pillole informative a cui ti sei iscritto:<br><br>' \
                                 f'<ul>{"".join([f"<li>{subscription}</li>" for subscription in subscriptions])}</ul><br><br>' \
                                 f'Grazie per la tua partecipazione.<br><br>' \
                                 f'Il team di MediaMatrixHub',
                    list_of_bcc_email_addresses=[DEBUG_EMAIL],
                )

    else:
        form = EventParticipationForm()
        # Fetch existing participations for the subscriber to mark them in the form
        existing_participations = EventParticipation.objects.filter(subscriber=subscriber)
        for participation in existing_participations:
            form.fields[f'event_{participation.event.id}'].initial = True

    # return render(request, 'events/event_participation.html', {'form': form})

    return render(request, 'subscribers/manage_subscription.html', {'subscriber': subscriber, 'form': form})


def subscriber_logout(request):
    request.session['subscriber_id'] = None

    return redirect('subscriber-login')
