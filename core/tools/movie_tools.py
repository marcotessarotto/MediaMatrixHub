import re
import datetime

from moviepy import VideoFileClip


def get_video_duration(video_path):
    clip = VideoFileClip(video_path)
    duration = datetime.timedelta(seconds=int(clip.duration))
    return duration


def get_video_resolution(video_path):
    """
    Return tuple containing video resolution (width, height) for the given video file.
    """
    with VideoFileClip(video_path) as video:
        width, height = video.size
    return width, height


def extract_text_from_vtt(data: str) -> str:
    """
    Extracts the text from a VTT file, removing timestamps and UUIDs
    :param data:
    :return: The extracted text
    """
    # Split the input data by lines
    lines = data.split('\n')

    # Define a regular expression pattern for matching timestamps
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}')

    # Define a regular expression pattern for matching UUIDs followed by a hyphen and a number
    uuid_pattern = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}-\d+')

    # Initialize an empty list to hold the text parts
    text_parts = []

    # Iterate over the lines, using the regex to skip timestamps and UUIDs
    for line in lines:
        if not timestamp_pattern.match(line) and not uuid_pattern.match(line) and not line.startswith(
                ('WEBVTT', 'NOTE', 'STYLE', 'REGION')) and line.strip() != '':
            # The line is part of the text, add it to the list
            text_parts.append(line.strip())

    # Join the text parts with a space and return
    return ' '.join(text_parts)
