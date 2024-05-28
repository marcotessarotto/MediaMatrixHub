import time
import uuid

import PIL
from django.core.files.base import ContentFile
from django.db.models import F, Count
from django.utils import timezone
from django.utils.html import format_html
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _

from core.image_tools import resize_image_if_needed

from django.db import models

from PIL import Image
from pdf2image import convert_from_path
import io
import os


class Tag(models.Model):
    tag = models.CharField(max_length=100)

    # slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


class Structure(models.Model):
    DIREZIONE = 0
    SERVIZIO = 1
    HUB = 2
    POSIZIONE_ORGANIZZATIVA = 3
    COORDINAMENTO = 4
    STRUCTURE_TYPE_CHOICES = [
        (DIREZIONE, 'Direzione'),
        (SERVIZIO, 'Servizio'),
        (HUB, 'Hub'),
        (POSIZIONE_ORGANIZZATIVA, 'Posizione Organizzativa'),
        (COORDINAMENTO, 'Coordinamento'),
    ]
    name = models.CharField(max_length=200)
    uaf = models.CharField(max_length=20, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    structure_type = models.IntegerField(choices=STRUCTURE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    referente = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    ROLE_CHOICES = [
        ('dirigente', 'Dirigente'),
        ('posizione_organizzativa', 'Posizione Organizzativa'),
        ('', 'None'),  # Representing no role with an empty string
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='', blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"


def calc_directory_path(instance, filename):
    now_ms = int(time.time_ns() / 1000)

    return f"{now_ms}/{filename}"


# define new class AutomaticPreviewImage
class AutomaticPreviewImage(models.Model):
    image = models.ImageField(upload_to=calc_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AutomaticPreviewImage {self.id} - Created at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.image:
            return

        # Open the image
        image = PIL.Image.open(self.image)

        # Resize the image if necessary
        image = resize_image_if_needed(image)

        # Save the image
        temp_image = io.BytesIO()
        image.save(temp_image, format='JPEG')
        temp_image.seek(0)

        self.image.save(
            os.path.basename(self.image.name),
            ContentFile(temp_image.read()),
            save=False
        )

        super().save(*args, **kwargs)


class Media(models.Model):
    title = models.CharField(max_length=1024)
    description = CKEditor5Field('description', blank=True, config_name='extends')

    authors = models.TextField(blank=True, null=True, verbose_name=_("Authors"))

    enabled = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    ref_token = models.UUIDField(default=uuid.uuid4)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, blank=True, null=True)

    preview_image = models.ImageField(upload_to=calc_directory_path, blank=True, null=True,
                                      verbose_name=_("Immagine di preview"))
    # list of automated preview images
    automatic_preview_images = models.ManyToManyField(AutomaticPreviewImage, blank=True)

    # Field to select cover image
    cover_image = models.ForeignKey(AutomaticPreviewImage, related_name='cover_for_media', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Cover Image"),
                                    related_query_name='cover_image')

    fulltext_search_data = models.TextField(blank=True, verbose_name=_("Dati per la ricerca fulltext"))

    raw_transcription_file = models.FileField(upload_to=calc_directory_path, null=True, blank=True,
                                              verbose_name=_("File Trascrizione Raw"))
    # raw_transcription = models.TextField(blank=True, verbose_name=_("Trascrizione raw"))
    TRANSCRIPTION_TYPE_CHOICES = [
        ('vtt', _("vtt")),
        ('text', _("Testo")),
    ]
    transcription_type = models.CharField(max_length=100, choices=TRANSCRIPTION_TYPE_CHOICES, default="vtt",
                                          verbose_name=_("Tipo Trascrizione"))
    is_transcription_available = models.BooleanField(default=False)

    publication_date = models.DateField(null=True, blank=True, verbose_name=_("Publication Date"))

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def has_fulltext_search_data(self):
        """Check if the Video instance has fulltext_search_data."""
        return bool(self.fulltext_search_data)

    class Meta:
        abstract = True
        # pass

    def is_video(self):
        return False

    def is_document(self):
        return False

    def has_tags(self):
        return self.tags.exists()

    def get_associated_image(self):
        # if self.preview_image:
        #     print(f"Associated image: {self.preview_image}")
        #     print(f"Associated image URL: {self.preview_image.url}")
        #
        # if self.cover_image:
        #     print(f"Associated cover image: {self.cover_image}")
        #     print(f"Associated cover image URL: {self.cover_image.image.url}")

        if self.preview_image:
            return self.preview_image
        elif self.cover_image and self.cover_image.image:
            return self.cover_image.image
        else:
            return None

        # return self.preview_image or self.cover_image.image


class Document(Media):
    categories = models.ManyToManyField('core.Category', through='DocumentCategory')
    document_file = models.FileField(upload_to=calc_directory_path, )

    cover_image = models.ForeignKey(AutomaticPreviewImage, related_name='cover_for_document', on_delete=models.SET_NULL,
                                    blank=True, null=True, verbose_name=_("Cover Image"))

    # version = models.CharField(max_length=255, blank=True, verbose_name=_("Version"))
    # doi = models.CharField(max_length=255, blank=True, verbose_name=_("Document Identifier (DOI)"))
    # accessibility_info = models.TextField(blank=True, verbose_name=_("Accessibility Information"))
    # file_checksum = models.CharField(max_length=255, blank=True, verbose_name=_("File Checksum"))
    # Consider adding methods for preview generation, search optimization, and file integrity verification

    def __str__(self):
        return self.title

    def is_document(self):
        return True

    def is_pdf(self):
        return self.document_file.name.endswith('.pdf')

    def generate_pdf_preview(self):
        """
        Generates a preview image for a PDF document.
        """
        try:
            # Convert the first page of the PDF to an image
            pages = convert_from_path(self.document_file.path, first_page=1, last_page=1)
            if pages:
                first_page_image = pages[0]

                # Check and resize if necessary
                first_page_image = resize_image_if_needed(first_page_image)

                # Save the image to a temporary location
                temp_image = io.BytesIO()
                first_page_image.save(temp_image, format='JPEG')
                temp_image.seek(0)

                # Save the image to the preview_image field
                self.preview_image.save(
                    os.path.splitext(self.document_file.name)[0] + '_preview.jpg',
                    ContentFile(temp_image.read()),
                    save=False
                )
        except Exception as e:
            print(f"Error generating PDF preview: {e}")

    # is the instance a document associated to a Video instance?
    def is_associated_with_video(self):
        return self.videodocument_set.exists()


class VideoDocument(models.Model):
    """This model is used to associate documents to videos."""
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    # description = models.TextField(blank=True, null=True)  # Optional description field
    order = models.PositiveIntegerField(default=0)  # Field to specify the order

    class Meta:
        ordering = ['order']  # Orders the documents by the 'order' field
        unique_together = ('video', 'document', 'order')  # Optional: ensures unique combinations


class Video(Media):
    categories = models.ManyToManyField('core.Category', through='VideoCategory')

    video_file = models.FileField(upload_to=calc_directory_path, )
    duration = models.DurationField(null=True, blank=True)
    start_time = models.DurationField(null=True, blank=True)
    stop_time = models.DurationField(null=True, blank=True)

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    documents = models.ManyToManyField('Document', through='VideoDocument', blank=True)

    cover_image = models.ForeignKey(AutomaticPreviewImage, related_name='cover_for_video', on_delete=models.SET_NULL,
                                    blank=True, null=True, verbose_name=_("Cover Image"))

    def __str__(self):
        return self.title

    def first_category(self):
        # Fetch the first associated category, if any
        try:
            first_category = self.categories.all().order_by('mediacategory__order').first()
            if first_category:
                print(f"First category: {first_category.name}")
            else:
                print("This media instance has no associated categories.")

            return first_category
        except Category.DoesNotExist:
            print("This media instance has no associated categories.")
            return None

    def get_ordered_documents_through_videodocument(self):
        """
        Retrieves the VideoDocument instances associated with this video,
        ordered by the 'order' field. This method allows access to the associated
        documents along with the extra fields (like 'description' and 'order')
        defined in the VideoDocument model.
        """
        return VideoDocument.objects.filter(video=self).order_by('order').select_related('document')

    def is_video(self):
        return True


class VideoPill(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)
    start_time = models.DurationField()
    stop_time = models.DurationField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Playlist(models.Model):
    videos = models.ManyToManyField(Video, through='PlaylistVideo')

    def __str__(self):
        return f"Playlist {self.id}"


class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class Image(models.Model):
    image_file = models.ImageField(upload_to=calc_directory_path, )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image {self.id} - Created at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(verbose_name=_("Descrizione"), blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name=_("Parent Category"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True, verbose_name=_("Icon"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_("Meta Description"))
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Keywords"))

    def get_children_categories(self):
        """Returns all child categories of this category."""
        return self.children.all().order_by('order')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    # define a class method to get all the categories that have no parent
    @classmethod
    def get_root_categories(cls):
        return cls.objects.filter(parent=None).filter(is_active=True).order_by('order')

    @classmethod
    def get_categories_hierarchy_html(cls):
        def render_category_row(category, level=0):
            indent = '&nbsp;' * 4 * level
            row = f"<tr><td>{indent}{category.name}</td><td>{category.description}</td><td>{category.is_active}</td></tr>"
            for child in category.get_children_categories().filter(is_active=True):
                row += render_category_row(child, level + 1)
            return row

        # Get top-level categories (those without a parent)
        top_categories = Category.objects.filter(parent__isnull=True).filter(is_active=True).order_by('order')

        # Render table headers
        table = "<table><thead><tr><th>Name</th><th>Description</th><th>Is Active</th></tr></thead><tbody>"
        for category in top_categories:
            table += render_category_row(category)
        table += "</tbody></table>"
        return format_html(table)

    @classmethod
    def get_categories_hierarchy_html_v2(cls):
        def render_category_row(category, level=0):
            indent = '&nbsp;' * 12 * level
            row = f"<tr><td>{indent}{category.name}</td></tr>"
            for child in category.get_children_categories().filter(is_active=True):
                row += render_category_row(child, level + 1)
            return row

        # Get top-level categories (those without a parent)
        top_categories = Category.objects.filter(parent__isnull=True).filter(is_active=True).order_by('order')

        # Render table headers
        table = "<table><thead><tr><th>Name</th></tr></thead><tbody>"
        for category in top_categories:
            table += render_category_row(category)
        table += "</tbody></table>"
        return format_html(table)


class DocumentCategory(models.Model):
    media = models.ForeignKey('core.Document', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.media.title} - {self.category.name} - Order {self.order}"


class VideoCategory(models.Model):
    media = models.ForeignKey(Video, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.media.title} - {self.category.name} - Order {self.order}"


class MessageLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    original_uri = models.CharField(max_length=2048, blank=True, default='-')  # Long URLs
    http_referer = models.CharField(max_length=2048, blank=True, default='-')  # HTTP referer URL
    http_user_agent = models.CharField(max_length=1024, blank=True, default='unknown')  # User agent
    http_real_ip = models.GenericIPAddressField(blank=True, null=True, default='unknown')  # IP Address
    http_cookie = models.CharField(max_length=1024, blank=True, default='-')  # Cookie

    # valid = models.BooleanField(default=False)
    # processed = models.BooleanField(default=False)

    # message = models.ForeignKey(Message, on_delete=models.CASCADE, blank=True, null=True)

    @classmethod
    def create_new_message_log(cls, log_dict):
        """
        Create a new message log record with the given log dictionary.
        :param log_dict: Dictionary containing log information
        :return: MessageLog instance
        """

        message_log = cls(
            original_uri=log_dict.get('original_uri', '-'),
            http_referer=log_dict.get('http_referer', '-'),
            http_user_agent=log_dict.get('http_user_agent', 'unknown'),
            http_real_ip=log_dict.get('http_real_ip', 'unknown'),
            http_cookie=log_dict.get('http_cookie', '-'),
        )

        message_log.save()
        return message_log

    def __str__(self):
        return f"MessageLog #{self.id} {self.created_at} "


class VideoPlaybackEvent(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)  # To accommodate both IPv4 and IPv6 addresses
    timestamp = models.DateTimeField(default=timezone.now)
    is_user_authenticated = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Playback event for {self.video} from IP {self.ip_address} at {self.timestamp}"

    @classmethod
    def get_count_distinct_ip_addresses_for_each_video(cls):
        """Class method to count distinct IP addresses for each video, including video title."""
        return cls.objects \
            .annotate(video_title=F('video__title')) \
            .values('video_title') \
            .annotate(distinct_ip_count=Count('ip_address', distinct=True)) \
            .order_by('video_title')

    @classmethod
    def get_count_events_for_each_video(cls):
        """Class method to count events for each video, including video title."""
        return cls.objects \
            .values('video__title') \
            .annotate(event_count=Count('id')) \
            .order_by('video__title')


class VideoCounter(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    playback_event_counter = models.IntegerField(default=0)

    def __str__(self):
        return f"Counter for {self.video} - playback_event_counter: {self.playback_event_counter}"

    def inc_playback_event_counter(self):
        self.playback_event_counter += 1
        self.save(update_fields=['playback_event_counter'])

    @classmethod
    def check_create_counter(cls, video_id):
        """
        Check if a counter for the given video ID exists. If it doesn't, create a new counter.
        :param video_id: The ID of the video.
        :return: VideoCounter instance
        """
        try:
            return VideoCounter.objects.get(video_id=video_id)
        except VideoCounter.DoesNotExist:
            return VideoCounter.objects.create(video_id=video_id)


def get_category_name_documents(category_name: str):
    """
    Returns all Documents belonging to a certain category that are not associated with any Video.

    Args:
        category_name (str): The name of the category.

    Returns:
        QuerySet: A queryset of Documents that are in the specified category and not associated with any Video.
    """
    return Document.objects.filter(
        categories__name=category_name
    ).exclude(
        videodocument__isnull=False
    )


def get_category_documents(category: Category):
    """
    Returns all Documents belonging to a certain category that are not associated with any Video.

    Args:
        category (Category): The Category instance.

    Returns:
        QuerySet: A queryset of Documents that are in the specified category and not associated with any Video.
    """
    return Document.objects.filter(
        categories=category
    ).exclude(
        videodocument__isnull=False
    )
