from django.urls import path
from django.conf.urls.static import static

from core.views import ShowHomeWithCategory, SearchHomeWithCategory

urlpatterns = [
    path('c/<str:category_name>/search/', SearchHomeWithCategory.as_view(), name='search-category-home'),
    path('c/<str:category_name>/', ShowHomeWithCategory.as_view(), name='show-category-home'),
]
