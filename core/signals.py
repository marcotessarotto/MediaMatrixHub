from django.core.files.storage import default_storage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import Document, Video
from core.tools.movie_tools import get_video_resolution, get_video_duration, extract_text_from_vtt


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

        # Save the processed text to fulltext_search_data using instance.save(update_fields=['fulltext_search_data'])
        # This method only updates the specified fields, preventing the post_save signal from being triggered again.
        instance.fulltext_search_data = processed_text
        instance.save(update_fields=['fulltext_search_data'])

        # Reconnect the signal
        # post_save.connect(update_fulltext_search_data, sender=sender)

        print(f"Fulltext search data updated for #{instance.id} {instance.title}")


@receiver(post_save, sender=Document)
def generate_preview_image(sender, instance, created, **kwargs):
    """
    Signal handler to generate a preview image for the Document instance if it's a PDF and no preview_image is defined.
    """
    if not instance.preview_image and instance.is_pdf():
        instance.generate_pdf_preview()
        instance.save()


# Signal to delete the associated document_file when a Document instance is deleted
@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    if instance.document_file:
        if default_storage.exists(instance.document_file.path):
            default_storage.delete(instance.document_file.path)


@receiver(post_delete, sender=Video)
def delete_video_file(sender, instance, **kwargs):
    if instance.video_file:
        if default_storage.exists(instance.video_file.path):
            default_storage.delete(instance.video_file.path)


