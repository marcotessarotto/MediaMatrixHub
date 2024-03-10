from django.urls import path
from django.conf.urls.static import static

from core.views import ShowHomeWithCategory, SearchHomeWithCategory, get_preview_image, proxy_django_auth, \
    video_player_event

urlpatterns = [
    path('c/<str:category_name>/search/', SearchHomeWithCategory.as_view(), name='search-category-home'),
    path('c/<str:category_name>/', ShowHomeWithCategory.as_view(), name='show-category-home'),
    path('get_preview_image/<str:ref_token>/', get_preview_image, name='get_preview_image'),
    path('proxy_django_auth/', proxy_django_auth, name='proxy_django_auth'),
    path('video_player_event/', video_player_event, name='video_player_event'),
]
