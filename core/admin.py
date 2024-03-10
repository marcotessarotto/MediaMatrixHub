from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Video, VideoPill, Playlist, Structure, Person, Tag, PlaylistVideo, Category, VideoCategory, \
    Document, VideoDocument, DocumentCategory


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
    list_display = ('id', 'title', 'display_categories', 'duration', 'enabled', 'has_fulltext_search_data', 'structure', 'created_at',)
    list_filter = ('enabled', 'structure', 'tags')
    search_fields = ('title', 'description')
    inlines = [TagInline, VideoCategoryInline, VideoDocumentInline]

    def display_categories(self, obj):
        """Display categories related to the video."""
        categories = obj.categories.all()
        return ', '.join([category.name for category in categories])
    display_categories.short_description = "Categories"

    # exclude = ('owner',)


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
    list_display = ('title', 'enabled', 'ref_token', 'preview_image_display', 'document_file_link')
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




