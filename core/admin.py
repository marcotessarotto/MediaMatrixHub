from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Video, VideoPill, Playlist, Structure, Person, Tag, PlaylistVideo, Category, VideoCategory, \
    Document, VideoDocument


class PlaylistVideoInline(admin.TabularInline):
    model = PlaylistVideo
    extra = 1


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
    list_display = ('id', 'title', 'display_categories', 'duration', 'enabled', 'structure', 'created_at',)
    list_filter = ('enabled', 'structure', 'tags')
    search_fields = ('title', 'description')
    inlines = [TagInline, VideoCategoryInline, VideoDocumentInline]

    def display_categories(self, obj):
        """Display categories related to the video."""
        categories = obj.categories.all()
        return ', '.join([category.name for category in categories])
    display_categories.short_description = "Categories"

    # exclude = ('owner',)

    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:  # Check if this is a new object being created
    #         obj.owner = request.user  # Set the owner to the currently logged-in user
    #     super().save_model(request, obj, form, change)


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


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'enabled', 'ref_token', 'cover_image')  # Customize as needed
    search_fields = ['title', 'description']
    list_filter = ('enabled', 'categories')

