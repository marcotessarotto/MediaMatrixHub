
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.http import HttpResponse
from django.shortcuts import render

from core.models import Category, Media, Video

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


class ShowHomeWithCategory(CreateView):

    def get(self, request, category_name, *args, **kwargs):

        category = get_object_or_404(Category, name=category_name)

        print(f"Category: {category}")

        # Querying each concrete model separately
        videos_list = Video.objects.filter(categories=category)
        print(f"list of videos: {videos_list}")

        context = {
            'category_name': category,
            'videos_list': videos_list,
            'page_header': 'Category Home',
        }

        return render(request, 'core/gallery-v2.html', context)

    def post(self, request, *args, **kwargs):
        pass