# python
from django.db.models.functions import TruncDate
from collections import OrderedDict
from core.models import VideoPlaybackEvent

def get_video_playback_events_totals():
    """
    Returns an ordered dictionary where the key is Video.title and the value is the number of unique
    VideoPlaybackEvent occurrences, counted as distinct (video, ip_address, day) tuples.
    Only events where is_user_authenticated is True and the related video has a category with name
    'pillole informative' are considered. Results are ordered by Video.id.
    """
    qs = VideoPlaybackEvent.objects.annotate(
        event_day=TruncDate('timestamp')
    ).filter(
        is_user_authenticated=False,
        video__categories__name='pillole informative'
    ).values(
        'video__id', 'video__title', 'ip_address', 'event_day'
    ).distinct().order_by('video__id')

    grouped = {}
    for record in qs:
        video_id = record['video__id']
        if video_id in grouped:
            grouped[video_id]['count'] += 1
        else:
            grouped[video_id] = {
                'title': record['video__title'],
                'count': 1,
            }

    totals = OrderedDict()
    for video_id in sorted(grouped.keys()):
        totals[grouped[video_id]['title']] = grouped[video_id]['count']

    return totals