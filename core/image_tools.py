from PIL.Image import Resampling

from mediamatrixhub.settings import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT


def resize_image_if_needed(image):
    """
    Resize the image if it exceeds the maximum dimensions.
    """

    from PIL.Image import Image

    if image.width > MAX_IMAGE_WIDTH or image.height > MAX_IMAGE_HEIGHT:
        # Calculate the new size preserving the aspect ratio
        ratio = min(MAX_IMAGE_WIDTH / image.width, MAX_IMAGE_HEIGHT / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        return image.resize(new_size, Resampling.LANCZOS)
    return image