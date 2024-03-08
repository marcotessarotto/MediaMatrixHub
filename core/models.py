import time
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _

from core.movie_tools import get_video_duration, extract_text_from_vtt

from django.db import models
from django.contrib.auth.models import User


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
    description = CKEditor5Field('Text', blank=True, config_name='extends')

    # categories = models.ManyToManyField('core.Category', through='MediaCategory')

    enabled = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    ref_token = models.UUIDField(default=uuid.uuid4)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, blank=True, null=True)

    cover_image = models.ImageField(upload_to=calc_directory_path, blank=True, null=True,
                                    verbose_name=_("Immagine di copertina"))

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

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True
        # pass


# @receiver(post_save, sender='core.Video')
# def update_fulltext_search_data(sender, instance, **kwargs):
#     # Check if transcription is available and the raw_transcription_file has been specified
#     if instance.is_transcription_available and instance.raw_transcription_file:
#         # Read the content from the file
#         vtt_content = instance.raw_transcription_file.read().decode('utf-8')
#
#         # Process the content to extract text
#         processed_text = extract_text_from_vtt(vtt_content)
#
#         # Save the processed text to fulltext_search_data
#         instance.fulltext_search_data = processed_text
#         instance.save()
#
#         print(f"Fulltext search data updated for {instance.title}")


class Document(Media):
    categories = models.ManyToManyField('core.Category', through='DocumentCategory')
    document_file = models.FileField(upload_to=calc_directory_path, )

    def __str__(self):
        return self.title


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


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        instance.duration = get_video_duration(instance.video_file.path)
        instance.stop_time = instance.duration
        instance.save()


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
