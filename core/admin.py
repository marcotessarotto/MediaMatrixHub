from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import path

from mediamatrixhub.admin_utils import ExportExcelMixin
from .models import Video, VideoPill, Playlist, Structure, Person, Tag, PlaylistVideo, Category, VideoCategory, \
    Document, VideoDocument, DocumentCategory, MessageLog, VideoPlaybackEvent, VideoCounter


class PlaylistVideoInline(admin.TabularInline):
    model = PlaylistVideo
    extra = 1


class TagListFilter(admin.SimpleListFilter):
    title = _('tags')
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        tags = Tag.objects.all()
        return [(tag.id, tag.tag) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__id=self.value())
        return queryset


class TagInline(admin.TabularInline):
    model = Video.tags.through
    extra = 1


class VideoCategoryInline(admin.TabularInline):
    model = VideoCategory
    extra = 1  # Specifies the number of blank forms the inline formset will display


class VideoDocumentInline(admin.TabularInline):
    model = VideoDocument
    extra = 1  # How many rows to show by default
    # Specify any additional fields you want to include


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'display_categories', 'duration', 'enabled', 'has_fulltext_search_data', 'structure', 'created_at',
    )
    list_filter = ('enabled', 'structure', TagListFilter)  # Use custom tag filter
    search_fields = ('title', 'description')
    inlines = [TagInline, VideoCategoryInline, VideoDocumentInline]

    def display_categories(self, obj):
        """Display categories related to the video."""
        categories = obj.categories.all()
        return ', '.join([category.name for category in categories])

    display_categories.short_description = "Categories"


@admin.register(VideoPill)
class VideoPillAdmin(admin.ModelAdmin):
    list_display = ('video', 'start_time', 'stop_time')
    search_fields = ('video__title',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    inlines = [PlaylistVideoInline]


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'structure_type', 'parent', 'referente')
    list_filter = ('structure_type',)
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email')
    search_fields = ('name', 'surname', 'email')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    search_fields = ('tag',)


# Unregister the auto-generated through model admin if needed
# admin.site.unregister(Video.tags.through)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at', 'order')
    list_filter = ('is_active', 'created_at', 'parent')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name',)
    fieldsets = (
        (_("Category Details"), {'fields': ('name', 'description', 'slug', 'parent', 'is_active', 'icon')}),
        (_("Hierarchy and Ordering"), {'fields': ('order',)}),
        (_("SEO Settings"), {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        (_("Dates"), {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_form(self, request, obj=None, **kwargs):
        form = super(CategoryAdmin, self).get_form(request, obj, **kwargs)
        # Custom form modifications can go here
        return form


class DocumentCategoryInline(admin.TabularInline):
    model = DocumentCategory
    extra = 1  # Specifies the number of blank forms the inline formset will display


class DocumentTagInline(admin.TabularInline):
    model = Document.tags.through
    extra = 1


class CategoryListFilter(admin.SimpleListFilter):
    title = 'category'  # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
    parameter_name = 'category'  # Parameter for the filter that will be used in the URL query.

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each tuple is the coded value for the option that will appear in the URL query.
        The second element is the human-readable name for the option that will appear in the right sidebar.
        """
        categories = Category.objects.all()
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in the query string and retrievable via `self.value()`.
        """
        if self.value():
            return queryset.filter(categories__id=self.value())
        return queryset


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'enabled', 'ref_token', 'display_categories', 'preview_image_display', 'document_file_link')
    search_fields = ['title', 'description', 'document_file']
    list_filter = ('enabled', CategoryListFilter)  # Use the class directly without quotes
    inlines = [DocumentTagInline, DocumentCategoryInline]

    def preview_image_display(self, obj):
        if obj.preview_image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.preview_image.url)
        return "No image"

    preview_image_display.short_description = 'Cover Image'

    def document_file_link(self, obj):
        if obj.document_file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.document_file.url)
        return "No file"

    document_file_link.short_description = 'Document File'

    def display_categories(self, obj):
        """Display categories related to the document."""
        categories = obj.categories.all()
        return ', '.join([category.name for category in categories])

    display_categories.short_description = "Categories"


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ('id', 'created_at', 'http_real_ip', 'original_uri')
    list_filter = ['created_at', 'original_uri']

    actions = ["export_as_excel"]


class VideoPlaybackEventAdmin(admin.ModelAdmin):
    list_display = ('video', 'ip_address', 'timestamp', 'is_user_authenticated', 'username')
    list_filter = ('is_user_authenticated', 'timestamp')
    search_fields = ('ip_address', 'username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('video', 'ip_address', 'is_user_authenticated', 'username')
        return self.readonly_fields

    # Custom admin URL for displaying counts
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('video-ip-counts/', self.admin_site.admin_view(self.video_ip_counts)),
        ]
        return my_urls + urls

    def video_ip_counts(self, request, queryset):
        # Perform your aggregation query here
        counts = VideoPlaybackEvent.objects.values('video', 'ip_address').annotate(total=Count('id')).order_by('video')

        query1 = VideoPlaybackEvent.get_count_distinct_ip_addresses_for_each_video().all()
        # print("query1: ", query1)

        query2 = VideoPlaybackEvent.get_count_events_for_each_video()
        # print("query2: ", query2)

        context = {
            'counts': counts,
            'query1': query1,
            'query2': query2
                   }
        return render(request, 'admin/video_ip_counts.html', context)

    actions = ["video_ip_counts"]


admin.site.register(VideoPlaybackEvent, VideoPlaybackEventAdmin)


class VideoCounterAdmin(admin.ModelAdmin):
    list_display = ('video', 'playback_event_counter')
    search_fields = ('video__id', 'video__title')  # Assuming your Video model has a 'title' field
    readonly_fields = ('playback_event_counter',)

    def has_add_permission(self, request):
        # Optionally disable adding new entries through admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Optionally disable deleting entries through admin
        return True


admin.site.register(VideoCounter, VideoCounterAdmin)
