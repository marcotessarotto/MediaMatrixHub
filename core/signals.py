import PIL
import io

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from moviepy.editor import VideoFileClip

from core.models import Document, Video, AutomaticPreviewImage
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


def delete_automatic_preview_images(sender, instance, **kwargs):
    for preview_image in instance.automatic_preview_images.all():
        preview_image.delete()


def extract_frame(video_path, t):
    with VideoFileClip(video_path) as video:
        frame = video.get_frame(t)
        frame_image = PIL.Image.fromarray(frame)
        temp_image = io.BytesIO()
        frame_image.save(temp_image, format='JPEG')
        temp_image.seek(0)
        return ContentFile(temp_image.read(), name=f"frame_{t}.jpg")


# @receiver(post_save, sender=Video)
# def generate_preview_images(sender, instance, created, **kwargs):
#
#     print(f"generate_preview_images - instance: {instance.id}")
#
#     if instance.video_file:
#         # Reload the instance to ensure we get the latest data
#         instance.refresh_from_db()
#
#         for item in instance.automatic_preview_images.all():
#             print(f"item {item}")
#
#         # show count of automatic_preview_images
#         print(f"Automatic preview images count: {instance.automatic_preview_images.count()}")
#
#         if not instance.automatic_preview_images.exists():
#             video_path = instance.video_file.path
#             times = [5, 10, 15]
#             for t in times:
#                 try:
#                     frame_file = extract_frame(video_path, t)
#                     preview_image = AutomaticPreviewImage()
#                     preview_image.image.save(frame_file.name, frame_file)
#                     preview_image.save()
#                     instance.automatic_preview_images.add(preview_image)
#                 except Exception as e:
#                     print(f"Error extracting frame at {t} seconds: {e}")
#             instance.save()

#
# @receiver(post_save, sender=Video)
# def generate_preview_images_post_save(sender, instance, created, **kwargs):
#     if created:
#         instance._is_new = True
#     else:
#         instance._is_new = False
#
#
# @receiver(m2m_changed, sender=Video.automatic_preview_images.through)
# def generate_preview_images_m2m(sender, instance, action, **kwargs):
#     print("generate_preview_images_m2m")
#     if action == "post_add":
#         if instance.video_file:
#             if not instance.automatic_preview_images.exists():
#                 video_path = instance.video_file.path
#                 times = [5, 10, 15]
#                 for t in times:
#                     try:
#                         frame_file = extract_frame(video_path, t)
#                         preview_image = AutomaticPreviewImage()
#                         preview_image.image.save(frame_file.name, frame_file)
#                         preview_image.save()
#                         instance.automatic_preview_images.add(preview_image)
#                     except Exception as e:
#                         print(f"Error extracting frame at {t} seconds: {e}")
#
#                 # Debug logs
#                 for item in instance.automatic_preview_images.all():
#                     print(f"item {item}")
#
#                 # Show count of automatic_preview_images
#                 print(f"Automatic preview images count: {instance.automatic_preview_images.count()}")

