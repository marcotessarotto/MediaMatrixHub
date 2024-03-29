import time
import uuid

from django.db.models import F, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _

from core.tools.movie_tools import get_video_duration, extract_text_from_vtt, get_video_resolution

from django.db import models


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


@receiver(post_save, sender='core.Video')
def video_post_save(sender, instance, **kwargs):
    # if created:
    if (
        instance.video_file
        and not instance.duration
        and not instance.stop_time
        and kwargs.get('update_fields', None) != {'duration', 'stop_time', 'width', 'height'}
    ):
        print(f"Updating duration and stop_time for #{instance.id} {instance.title}")

        width, height = get_video_resolution(instance.video_file.path)
        print(f"Resolution: {width, height}")
        print(f"w: {width}, h: {height}")
        print(f"type of width: {type(width)}")
        instance.width = width
        instance.height = height

        instance.duration = get_video_duration(instance.video_file.path)
        instance.stop_time = instance.duration
        instance.save(update_fields=['duration', 'stop_time', 'width', 'height'])

        print(f"Duration and stop_time updated for #{instance.id} {instance.title}")


@receiver(post_save, sender='core.Video')
def update_fulltext_search_data(sender, instance, **kwargs):
    # Check if transcription is available, the raw_transcription_file has been specified,
    # and we are not already updating the fulltext_search_data to prevent recursion
    if (
        instance.is_transcription_available
        and instance.raw_transcription_file
        and kwargs.get('update_fields', None) != {'fulltext_search_data'}
    ):
        print(f"Updating fulltext search data for #{instance.id} {instance.title}")

        # Read the content from the file
        vtt_content = instance.raw_transcription_file.read().decode('utf-8')

        # Process the content to extract text
        processed_text = extract_text_from_vtt(vtt_content)

        # Temporarily disconnect the signal to prevent recursion
        # post_save.disconnect(update_fulltext_search_data, sender=sender)

        # Save the processed text to fulltext_search_data using instance.save(update_fields=['fulltext_search_data'])
        # This method only updates the specified fields, preventing the post_save signal from being triggered again.
        instance.fulltext_search_data = processed_text
        instance.save(update_fields=['fulltext_search_data'])

        # Reconnect the signal
        # post_save.connect(update_fulltext_search_data, sender=sender)

        print(f"Fulltext search data updated for #{instance.id} {instance.title}")


class Document(Media):
    categories = models.ManyToManyField('core.Category', through='DocumentCategory')
    document_file = models.FileField(upload_to=calc_directory_path, )

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


class VideoDocument(models.Model):
    """This model is used to associate documents to videos."""
    video = models.ForeignKey('Video', on_delete=models.CASCADE)
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)  # Optional description field
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