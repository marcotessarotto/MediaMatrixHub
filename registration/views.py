from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SubscriberLoginForm
from .models import Subscriber


def subscriber_login(request):
    if request.method == 'POST':
        form = SubscriberLoginForm(request.POST)
        if form.is_valid():
            matricola = form.cleaned_data['matricola']
            email = form.cleaned_data['email']
            try:
                subscriber = Subscriber.objects.get(matricola=matricola, email=email)
                # Simulate login by saving subscriber's ID in session (example)
                request.session['subscriber_id'] = subscriber.id
                return redirect('manage-subscription')
            except Subscriber.DoesNotExist:
                return redirect('login-error')
    else:
        form = SubscriberLoginForm()
    return render(request, 'subscribers/login.html', {'form': form})
