from django.contrib import admin
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from mediamatrixhub.admin_utils import ExportExcelMixin
from .models import Video, VideoPill, Playlist, Structure, Person, Tag, PlaylistVideo, Category, VideoCategory, \
    Document, VideoDocument, DocumentCategory, MessageLog, VideoPlaybackEvent, VideoCounter, AutomaticPreviewImage
from .forms import VideoAdminForm
from .signals import extract_frame
from .tools.movie_tools import get_video_resolution, get_video_duration


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
    form = VideoAdminForm

    list_display = (
        'id', 'title', 'display_categories', 'duration', 'enabled', 'has_fulltext_search_data', 'structure', 'created_at',
    )
    list_filter = ('enabled', 'structure', CategoryListFilter,)
    search_fields = ('title', 'description')
    inlines = [VideoCategoryInline, VideoDocumentInline]
    fields = (
        'title',
        'description',
        'authors',
        'enabled',
        'tags',
        'ref_token',
        'structure',
        'preview_image',
        'cover_image',
        # 'automatic_preview_images',
        'fulltext_search_data',
        'raw_transcription_file',
        'transcription_type',
        'is_transcription_available',
        'video_file',
        'publication_date',
        'duration',
        'start_time',
        'stop_time',
        'width',
        'height',
        'created_at',
        'updated_at'
    )
    readonly_fields = ('created_at', 'updated_at')
    change_form_template = "admin/video_change_form.html"  # Specify the custom template

    def display_categories(self, obj):
        """Display categories related to the video."""
        categories = obj.categories.all()
        return ', '.join([category.name for category in categories])

    display_categories.short_description = "Categories"

    def video_extract_frames(self, request, video_id):

        video = get_object_or_404(Video, pk=video_id)
        if video.video_file:
            video_path = video.video_file.path
            times = [5, 10, 15]
            for t in times:
                try:
                    frame_file = extract_frame(video_path, t)
                    preview_image = AutomaticPreviewImage()
                    preview_image.image.save(frame_file.name, frame_file)
                    preview_image.save()
                    video.automatic_preview_images.add(preview_image)
                except Exception as e:
                    self.message_user(request, f"Error extracting frame at {t} seconds: {e}", level='error')
            video.save()
            self.message_user(request, "Frames extracted successfully", level='success')
        else:
            self.message_user(request, "No video file found", level='error')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:video_id>/video_extract_frames/', self.admin_site.admin_view(self.video_extract_frames), name='video_extract_frames'),
            path('<path:video_id>/calculate_video_duration/', self.admin_site.admin_view(self.calculate_video_duration), name='calculate_video_duration'),
        ]

        print(f"custom_urls: {custom_urls}")
        return custom_urls + urls

    def render_change_form(self, request, context, *args, **kwargs):
        context['video_extract_frames_url'] = reverse('admin:video_extract_frames', args=[context['object_id']])
        context['calculate_video_duration_url'] = reverse('admin:calculate_video_duration', args=[context['object_id']])
        return super().render_change_form(request, context, *args, **kwargs)

    def calculate_video_duration(self, request, video_id):

        print(f"calculate_video_duration: {video_id}")

        video = get_object_or_404(Video, pk=video_id)
        if video.video_file:



            width, height = get_video_resolution(video.video_file.path)
            print(f"Resolution: {width, height}")
            print(f"w: {width}, h: {height}")
            print(f"type of width: {type(width)}")
            video.width = width
            video.height = height

            video.save()

            video.duration = get_video_duration(video.video_file.path)
            video.stop_time = video.duration
            video.save(update_fields=['duration', 'stop_time', 'width', 'height'])

            self.message_user(request, "Video duration calculated successfully", level='success')
        else:
            self.message_user(request, "No video file found", level='error')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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


class IsAssociatedWithVideoFilter(admin.SimpleListFilter):
    title = 'is associated with video'
    parameter_name = 'is_associated_with_video'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(video__isnull=False)
        if self.value() == 'no':
            return queryset.filter(video__isnull=True)
        return queryset


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'enabled', 'ref_token', 'is_associated_with_video', 'display_categories', 'preview_image_display', 'document_file_link')
    search_fields = ['title', 'description', 'document_file']
    list_filter = ('enabled', CategoryListFilter, IsAssociatedWithVideoFilter)  # Use the class directly without quotes
    inlines = [DocumentCategoryInline]

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


@admin.register(AutomaticPreviewImage)
class AutomaticPreviewImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'created_at', 'updated_at')
    readonly_fields = ('image_tag',)
    search_fields = ('id',)
    list_filter = ('created_at', 'updated_at')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return "No image"

    image_tag.short_description = 'Preview Image'