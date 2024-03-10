from core.models import MessageLog


def process_http_request(request):
    # get url from request
    url = request.build_absolute_uri()

    if request.META:
        try:
            log_dict = {
                'original_uri': url,
                'http_referer': request.META.get('HTTP_REFERER', '-'),
                'http_user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
                'http_real_ip': request.META.get('HTTP_X_REAL_IP', 'unknown'),
                'http_cookie': request.META.get('HTTP_COOKIE', '-'),
            }

            new_log = MessageLog.create_new_message_log(log_dict)

        except Exception as e:
            print(f"process_download_media_request - Exception: {e}")
    else:
        print("process_download_media_request - no request.META")