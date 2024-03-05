from django.urls import path
from django.conf.urls.static import static

from core.views import ShowHomeWithCategory, SearchHomeWithCategory, get_cover_image

urlpatterns = [
    path('c/<str:category_name>/search/', SearchHomeWithCategory.as_view(), name='search-category-home'),
    path('c/<str:category_name>/', ShowHomeWithCategory.as_view(), name='show-category-home'),
    path('get_cover_image/<str:ref_token>/', get_cover_image, name='get_cover_image'),
]
