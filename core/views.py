from django.http import HttpResponse
from django.shortcuts import render

from mediamatrixhub.view_tools import is_private_ip


# Create your views here.

def proxy_django_auth(request):
    """Used for authentication by nginx when accessing static media files."""

    # Get client IP address from request META
    # client_ip = request.META.get('REMOTE_ADDR', '')
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Check if the IP is private
    if is_private_ip(http_real_ip):
        # No authentication required for private IP addresses
        return HttpResponse(status=200)
    else:
        # Verify user is authenticated for public IP addresses
        if request.user.is_authenticated:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)

