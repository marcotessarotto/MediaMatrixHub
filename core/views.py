import os
import syslog

from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.http import HttpResponse, Http404
from django.shortcuts import render
import io
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont

from core.models import Category, Media, Video
from mediamatrixhub.settings import DEBUG

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
        http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

        # Check if the IP is private
        if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
            syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
            return render(request, 'core/show_generic_message.html',
                          {'message': "403 Forbidden - accesso consentito solo da intranet"}, status=403)

        category = get_object_or_404(Category, name=category_name)

        print(f"Category: {category}")

        # Querying each concrete model separately
        videos_list = Video.objects.filter(categories=category).filter(enabled=True)
        print(f"list of videos: {videos_list}")

        context = {
            'category_name': category,
            'videos_list': videos_list,
            'page_header': 'Category Home',
        }

        return render(request, 'core/gallery-v2.html', context)

    def post(self, request, *args, **kwargs):
        pass


class SearchHomeWithCategory(CreateView):
    def get(self, request, category_name, *args, **kwargs):
        raise Http404("This page does not exist")


def get_cover_image(request, ref_token):
    try:
        # Retrieve the video instance by ref_token
        video = Video.objects.get(ref_token=ref_token)

        width = video.width or 1920
        height = video.height or 1080

        font_size = height // 20

        text_height = height // 4

        # Prepare the image
        image = Image.new('RGB', (width, height), color=(73, 109, 137))
        d = ImageDraw.Draw(image)

        # Check if the specified font path exists
        font_path = "/usr/local/share/fonts/DecimaUNICASEReg01.otf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Fallback to a standard font available on Debian/Ubuntu
            # Make sure the 'fonts-dejavu-core' package is installed
            standard_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            font = ImageFont.truetype(standard_font_path, font_size)

        # Adding text to the image
        d.text((10, text_height), video.title, fill=(255, 255, 0), font=font, align="center")

        # Save the image to a bytes buffer
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        # Serve the image
        return HttpResponse(buffer, content_type='image/png')
    except Video.DoesNotExist:
        return HttpResponse('Video not found', status=404)