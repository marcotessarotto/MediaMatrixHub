from .models import Subscriber


def create_subscriber(email, name, surname, matricola):
    """
    Creates a new Subscriber instance and saves it to the database.

    Parameters:
    - email (str): The email of the subscriber.
    - name (str): The first name of the subscriber.
    - surname (str): The last name of the subscriber.
    - matricola (str): The matricola (unique identifier) of the subscriber.

    Returns:
    - subscriber (Subscriber): The newly created Subscriber instance.
    """
    subscriber = Subscriber(email=email, name=name, surname=surname, matricola=matricola)
    subscriber.save()
    return subscriber

