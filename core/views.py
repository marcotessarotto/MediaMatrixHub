import os
import syslog

from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView
from django.http import HttpResponse, Http404
from django.shortcuts import render
import io
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from PIL import Image, ImageDraw, ImageFont

from core.models import Category, Media, Video, VideoPlaybackEvent, VideoCounter, get_category_documents
from core.tools.stat_tools import process_http_request
from mediamatrixhub import settings
from mediamatrixhub.settings import DEBUG, APPLICATION_TITLE, TECHNICAL_CONTACT_EMAIL, TECHNICAL_CONTACT

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

    def get(self, request, category_slug, *args, **kwargs):
        http_real_ip = request.META.get('HTTP_X_REAL_IP', '')
        try:
            if not request.user.is_authenticated or not request.user.is_superuser:
                # Check if the IP is private
                if http_real_ip != '' and not is_private_ip(http_real_ip) and not settings.DEBUG:
                    syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
                    return render(request, 'core/show_generic_message.html',
                                  {'message': "403 Forbidden - accesso consentito solo da intranet"}, status=403)

            process_http_request(request)

            category = get_object_or_404(Category, slug=category_slug)

            # Querying each concrete model separately
            videos_list = Video.objects.filter(categories=category).filter(enabled=True)

            context = {
                'category': category,
                'videos_list': videos_list,
                'documents_list': get_category_documents(category),
                'page_header': 'Category Home',
                'APPLICATION_TITLE': settings.APPLICATION_TITLE,
                'TECHNICAL_CONTACT_EMAIL': settings.TECHNICAL_CONTACT_EMAIL,
                'TECHNICAL_CONTACT': settings.TECHNICAL_CONTACT,
            }

            return render(request, 'core/gallery-v2.html', context)
        except Category.DoesNotExist:
            return render(request, 'core/show_generic_message.html',
                          {'message': "Category not found"}, status=404)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR, f'Unexpected error: {str(e)}')
            return render(request, 'core/show_generic_message.html',
                          {'message': "An unexpected error occurred. Please try again later."}, status=500)

    def post(self, request, *args, **kwargs):
        pass


class SearchHomeWithCategory(CreateView):
    def get(self, request, category_slug, *args, **kwargs):
        raise Http404("This page does not exist")


class ShowCategories(CreateView):
    def get(self, request, *args, **kwargs):

        # get all the categories without parent
        categories = Category.objects.filter(parent=None)

        context = {
            'categories': categories,
            'page_header': 'Categories',
            'APPLICATION_TITLE': APPLICATION_TITLE,
            'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
            'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
        }

        return render(request, 'core/categories.html', context)


def get_preview_image(request, ref_token):
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


@require_POST
def video_player_event(request):
    ref_token = request.POST.get('ref_token')
    print(f"video_player_event - ref_token: {ref_token}")

    # get Video instance from ref_token
    video = Video.objects.get(ref_token=ref_token)
    print(f"video_player_event - video: {video}")

    # get real ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Create a new VideoPlaybackEvent instance
    VideoPlaybackEvent.objects.create(
        video=video,
        ip_address=http_real_ip,
        is_user_authenticated=request.user.is_authenticated,
        username=request.user.username if request.user.is_authenticated else None
    )

    video_counter = VideoCounter.check_create_counter(video.id)
    video_counter.inc_playback_event_counter()

    # Process the video URL as needed
    return JsonResponse({'status': 'success', 'message': 'ref_token received'})


def category_hierarchy_view(request):
    category_html_table = Category.get_categories_hierarchy_html()   #objects.first().get_html_table()  # Assuming there is at least one category
    return render(request, 'core/admin/category_hierarchy.html', {'category_html_table': category_html_table})

