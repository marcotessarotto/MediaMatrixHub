import syslog

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from mediamatrixhub.email_utils import send_simple_html_email
from mediamatrixhub.settings import DEBUG, DEBUG_EMAIL, SUBJECT_EMAIL, VIDEOTECA_URL, APPLICATION_TITLE, \
    TECHNICAL_CONTACT_EMAIL, TECHNICAL_CONTACT
from mediamatrixhub.view_tools import is_private_ip
from .forms import SubscriberLoginForm, EventParticipationForm
from .logic import create_event_log
from .models import Subscriber, InformationEvent, EventParticipation, EventLog


def subscriber_login(request):
    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
        return render(request, 'show_message.html', {'message': "403 Forbidden - accesso consentito solo da intranet"},
                      status=403)

    if request.method == 'POST':
        form = SubscriberLoginForm(request.POST)
        if form.is_valid():
            matricola = form.cleaned_data['matricola']
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(matricola=matricola, email=email)

                create_event_log(
                    event_type=EventLog.LOGIN_SUCCESS,
                    event_title="Subscriber login success",
                    event_data=f"matricola: {matricola} email: {email} http_real_ip: {http_real_ip}",
                )

                # login(request, user, backend=AUTHENTICATION_BACKENDS[0])

                # Simulate login by saving subscriber's ID in session (example)
                request.session['subscriber_id'] = subscriber.id
                return redirect('manage-subscription')
            except Subscriber.DoesNotExist:

                create_event_log(
                    event_type=EventLog.LOGIN_FAILED,
                    event_title="Subscriber login failed",
                    event_data=f"matricola: {matricola} email: {email} http_real_ip: {http_real_ip}",
                )

                messages.error(request, 'errore: matricola o email non validi')

    else:
        form = SubscriberLoginForm()
    return render(request, 'subscribers/login.html', {'form': form})


def manage_subscription(request):
    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        return render(request, 'show_message.html', {'message': "403 Forbidden - accesso consentito solo da intranet"},
                      status=403)

    # check request.session['subscriber_id'] and retrieve the subscriber instance
    subscriber_id = request.session.get('subscriber_id')
    if subscriber_id:
        subscriber = Subscriber.objects.get(id=subscriber_id)
    else:
        # send email to admin
        # redirect to login page
        return redirect('subscriber-login')

    additional_message = f'Puoi visualizzare le registrazioni delle precedenti pillole informative a questo indirizzo: ' \
                         f'<a href="{VIDEOTECA_URL}" target="_blank">{VIDEOTECA_URL}</a>'

    if request.method == 'POST':
        form = EventParticipationForm(request.POST)
        if form.is_valid():
            subscriptions = []

            for key, value in form.cleaned_data.items():
                event_id = key.split('_')[-1]
                event = InformationEvent.objects.get(id=event_id)

                if value:  # Checkbox is checked
                    # Check if the EventParticipation instance exists and update or create accordingly
                    EventParticipation.objects.update_or_create(
                        event=event,
                        subscriber=subscriber,
                        defaults={'event': event, 'subscriber': subscriber}
                    )

                    create_event_log(
                        event_type=EventLog.SUBSCRIPTION_SET,
                        event_title="Subscription set",
                        event_data=f"subscriber: {subscriber} event_id: {event_id}  event: {event}",
                        event_target=subscriber.email,
                    )

                    subscriptions.append(event.to_html_table_email())
                else:
                    EventParticipation.objects.filter(event=event, subscriber=subscriber).delete()

                    create_event_log(
                        event_type=EventLog.SUBSCRIPTION_REMOVED,
                        event_title="Subscription removed",
                        event_data=f"subscriber: {subscriber} event_id: {event_id}  event: {event}",
                        event_target=subscriber.email,
                    )

            messages.success(request,
                             'Iscrizioni alle pillole informative aggiornate con successo. '
                             'Ti ho inviato una email riassuntiva con i dettagli per accedere alle pillole informative.')

            # invia email riassuntiva all'utente
            if subscriptions:
                message_body = f'Ciao {subscriber.surname},<br><br>' \
                               f'hai aggiornato con successo le tue iscrizioni alle prossime pillole informative.<br><br>' \
                               f'Ecco un riepilogo delle future pillole informative a cui ti sei iscritto:<br><br>' \
                               f'{"<br><hr>".join([f"{subscription}" for subscription in subscriptions])}<br><br>' \
                               f"{additional_message}<br><br>" \
                               f'Grazie per la tua partecipazione.<br><br>'
            else:
                message_body = f'Ciao {subscriber.surname},<br><br>' \
                               f'hai aggiornato con successo le tue iscrizioni alle pillole informative.<br><br>' \
                               f'Ecco un riepilogo delle pillole informative a cui ti sei iscritto:<br><br>' \
                               f'Al momento non sei iscritto ad alcuna futura pillola informativa.<br><br>' \
                               f"{additional_message}<br><br>" \
                               f'Grazie per la tua partecipazione.<br><br>'

            message_subject = f'{SUBJECT_EMAIL} Riepilogo iscrizioni alle prossime pillole informative'

            if DEBUG:
                print(f"debug mode: fake sending email to {subscriber.email}")
                print(f"message: {message_body}  (debug mode)")

            send_simple_html_email(
                list_of_email_addresses=[subscriber.email],
                subject=message_subject,
                message_body=message_body,
                list_of_bcc_email_addresses=[DEBUG_EMAIL],
            )

            create_event_log(
                event_type=EventLog.EMAIL_SENT,
                event_title=message_subject,
                event_data=f"subscriber: {subscriber} email: {subscriber.email} {message_body}",
                event_target=subscriber.email,
            )

            return redirect('manage-subscription')

    else:

        current_date = timezone.now().date()

        form = EventParticipationForm(current_date=current_date)

        # Fetch existing participations for the subscriber to mark them in the form
        # existing_participations = EventParticipation.objects.filter(subscriber=subscriber)
        existing_participations = EventParticipation.objects.filter(
            subscriber=subscriber,
            event__event_date__gte=current_date
        )
        for participation in existing_participations:
            form.fields[f'event_{participation.event.id}'].initial = True

    context = {
        'subscriber': subscriber,
        'form': form,
        'additional_message': additional_message,
        'APPLICATION_TITLE': APPLICATION_TITLE,
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
    }

    return render(request, 'subscribers/manage_subscription.html', context)


def subscriber_logout(request):
    request.session['subscriber_id'] = None

    return redirect('subscriber-login')
