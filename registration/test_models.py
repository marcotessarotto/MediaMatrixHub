import pytest
from django.utils import timezone
from registration.models import InformationEvent, Subscriber, EventParticipation, EventLog, Category
from django.db.models import Count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "event_date, event_start_time, meeting_url, speaker, title, description, enabled, expected_html_contains", [
        # ID: HappyPath-1
        (timezone.now().date(), timezone.now().time(), "https://example.com/meeting", "John Doe", "Test Event",
         "Description of test event", True, "<table"),
        # ID: HappyPath-2
        (None, None, "https://example.com/meeting", "Jane Doe", "Another Test Event", "", False, "N/A"),
        # ID: EdgeCase-1
        (timezone.now().date(), timezone.now().time(), "", "Speaker", "Title", "Description", True, "Speaker"),
        # ID: ErrorCase-1
        (timezone.now().date(), timezone.now().time(), "not-a-url", "Speaker", "Title", "Description", True,
         "not-a-url"),
    ])
def test_information_event_to_html_table_email(event_date, event_start_time, meeting_url, speaker, title, description,
                                               enabled, expected_html_contains):
    # Arrange
    event = InformationEvent.objects.create(
        event_date=event_date,
        event_start_time=event_start_time,
        meeting_url=meeting_url,
        speaker=speaker,
        title=title,
        description=description,
        enabled=enabled
    )

    # Act
    html_table = event.to_html_table_email()

    # Assert
    assert expected_html_contains in html_table


@pytest.mark.django_db
@pytest.mark.parametrize("name, surname, matricola, expected_str", [
    # ID: HappyPath-1
    ("John", "Doe", "12345", "John Doe"),
    # ID: EdgeCase-1
    ("", "", "", " "),
    # ID: ErrorCase-1
    (None, None, None, "None None"),
])
def test_subscriber_str(name, surname, matricola, expected_str):
    # Arrange
    subscriber = Subscriber.objects.create(
        email="john.doe@example.com",
        name=name,
        surname=surname,
        matricola=matricola
    )

    # Act
    result_str = str(subscriber)

    # Assert
    assert result_str == expected_str


@pytest.mark.django_db
@pytest.mark.parametrize("event_type, event_title, event_data, event_target, expected_str_contains", [
    # ID: HappyPath-1
    (EventLog.LOGIN, "User Login", "User 'john' logged in successfully", None, "LOGIN"),
    # ID: EdgeCase-1
    (None, None, None, None, "None"),
    # ID: ErrorCase-1
    ("INVALID_TYPE", "Invalid Event", "Invalid data", "Invalid target", "INVALID_TYPE"),
])
def test_event_log_str(event_type, event_title, event_data, event_target, expected_str_contains):
    # Arrange
    event_log = EventLog.objects.create(
        event_type=event_type,
        event_title=event_title,
        event_data=event_data,
        event_target=event_target
    )

    # Act
    result_str = str(event_log)

    # Assert
    assert expected_str_contains in result_str


@pytest.mark.django_db
@pytest.mark.parametrize("category_name, category_description, expected_str", [
    # ID: HappyPath-1
    ("Technology", "All about tech", "Technology"),
    # ID: EdgeCase-1
    ("", "", ""),
    # ID: ErrorCase-1
    (None, None, "None"),
])
def test_category_str(category_name, category_description, expected_str):
    # Arrange
    category = Category.objects.create(
        name=category_name,
        description=category_description
    )

    # Act
    result_str = str(category)

    # Assert
    assert result_str == expected_str


@pytest.mark.django_db
@pytest.mark.parametrize("enabled, expected_count", [
    # ID: HappyPath-1
    (True, 1),
    # ID: HappyPath-2
    (False, 0),
])
def test_enabled_event_manager(enabled, expected_count):
    # Arrange
    InformationEvent.objects.create(
        event_date=timezone.now().date(),
        event_start_time=timezone.now().time(),
        meeting_url="https://example.com/meeting",
        speaker="John Doe",
        title="Test Event",
        description="Description of test event",
        enabled=enabled
    )

    # Act
    count = InformationEvent.enabled_events.count()

    # Assert
    assert count == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize("participation_count, expected_count", [
    # ID: HappyPath-1
    (5, 5),
    # ID: EdgeCase-1
    (0, 0),
])
def test_with_participation_count(participation_count, expected_count):
    # Arrange
    event = InformationEvent.objects.create(
        event_date=timezone.now().date(),
        event_start_time=timezone.now().time(),
        meeting_url="https://example.com/meeting",
        speaker="John Doe",
        title="Test Event",
        description="Description of test event",
        enabled=True
    )
    subscriber = Subscriber.objects.create(
        email="john.doe@example.com",
        name="John",
        surname="Doe",
        matricola="12345"
    )
    for _ in range(participation_count):
        EventParticipation.objects.create(event=event, subscriber=subscriber)

    # Act
    event_with_count = InformationEvent.enabled_events.with_participation_count().get(pk=event.pk)

    # Assert
    assert event_with_count.participation_count == expected_count
