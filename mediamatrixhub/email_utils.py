# Import smtplib for the actual sending function
import mimetypes
import os
import smtplib

# And imghdr to find the types of our images
# import imghdr
import syslog

# Here are the email package modules we'll need
from email.message import EmailMessage

from colorama import Fore

from mediamatrixhub.settings import DEBUG, FROM_EMAIL, EMAIL_HOST, DEBUG_EMAIL


def send_simple_html_email(list_of_email_addresses,
                           subject,
                           message_body,
                           list_of_cc_email_addresses=None,
                           list_of_bcc_email_addresses=None,
                           demo_msg=False):
    """Send an email with an HTML message body

    :param list_of_email_addresses: list (or set) of email addresses (strings)
    :param subject: subject of the email (string)
    :param message_body: message body of the email (string)
    :param list_of_cc_email_addresses: list (or set) of email addresses (strings) to be added to the Cc field (None by default)
    :param list_of_bcc_email_addresses: list (or set) of email addresses (strings) to be added to the Bcc field (None by default)
    :param demo_msg: if True, send the email only to MY_EMAIL (false by default)
    """

    if DEBUG:
        print(f"{Fore.YELLOW}send_simple_html_email: DEBUG is set, skipping{Fore.RESET}")
        return

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = DEBUG_EMAIL if demo_msg else '; '.join(list_of_email_addresses)

    if list_of_cc_email_addresses:
        # rimuovi eventuali destinatari già presenti in To dal Cc
        for email in list_of_email_addresses:
            if email in list_of_cc_email_addresses:
                list_of_cc_email_addresses.remove(email)

        if not demo_msg:
            msg['Cc'] = '; '.join(list_of_cc_email_addresses)
    # msg.set_content(message_body)
    # msg.add_header('Content-Type', 'text/html; charset=utf-8')

    if demo_msg:
        message_body += "<br><br>****DEMO MESSAGE****<br><br><br>" \
                        "destinatari:<br>" + str(list_of_email_addresses) + \
                        "<br><br>cc:<br>" + str(list_of_cc_email_addresses)

    part1 = MIMEText('questo messaggio ha un contenuto html', 'plain')
    part2 = MIMEText(message_body, "html")

    msg.attach(part1)
    msg.attach(part2)

    syslog.syslog(syslog.LOG_INFO,
                  f"send_simple_html_email: sending email to '{list_of_email_addresses}' subject='{msg['Subject']}'")

    # Send the email via SMTP server:
    with smtplib.SMTP(EMAIL_HOST) as s:
        # s.login(SENDER_EMAIL, APP_PASSWORD)
        # s.sendmail(me, you, msg.as_string())
        if demo_msg:
            s.sendmail(FROM_EMAIL, DEBUG_EMAIL, msg.as_string())
        else:
            if type(list_of_email_addresses) is set:
                list_of_email_addresses = list(list_of_email_addresses)
            if type(list_of_cc_email_addresses) is set:
                list_of_cc_email_addresses = list(list_of_cc_email_addresses)
            if type(list_of_bcc_email_addresses) is set:
                list_of_bcc_email_addresses = list(list_of_bcc_email_addresses)

            if list_of_cc_email_addresses is None:
                list_of_cc_email_addresses = []
            if list_of_bcc_email_addresses is None:
                list_of_bcc_email_addresses = []

            total_list = list_of_email_addresses + list_of_cc_email_addresses + list_of_bcc_email_addresses

            s.sendmail(FROM_EMAIL, total_list, msg.as_string())


class MyTemporaryFile:
    """
    A class representing a temporary file.

    Args:
        file_name (str): The name of the temporary file.
        content: The content of the temporary file.

    Methods:
        get_file_name: Get the name of the temporary file.
        get_content: Get the content of the temporary file.
    """

    def __init__(self, file_name, content):
        self.file_name = file_name
        self.content = content

    def get_file_name(self):
        return self.file_name

    def get_content(self):
        return self.content


def send_simple_html_email2(list_of_email_addresses,
                            subject,
                            message_body,
                            list_of_cc_email_addresses=None,
                            list_of_bcc_email_addresses=None,
                            file_name_list=None):
    """Send an email with an HTML message body

    :param list_of_email_addresses: list (or set) of email addresses (strings)
    :param subject: subject of the email (string)
    :param message_body: message body of the email (string)
    :param list_of_cc_email_addresses: list (or set) of email addresses (strings) to be added to the Cc field (None by default)
    :param list_of_bcc_email_addresses: list (or set) of email addresses (strings) to be added to the Bcc field (None by default)
    :param file_name_list: list of file names to be attached to the email (None by default)
    :param demo_msg: if True, send the email only to MY_EMAIL (false by default)
    """

    if DEBUG:
        print(f"{Fore.YELLOW}send_simple_html_email2: DEBUG is set, skipping{Fore.RESET}")
        return

    if type(list_of_email_addresses) is set:
        list_of_email_addresses = list(list_of_email_addresses)
    if type(list_of_cc_email_addresses) is set:
        list_of_cc_email_addresses = list(list_of_cc_email_addresses)
    if type(list_of_bcc_email_addresses) is set:
        list_of_bcc_email_addresses = list(list_of_bcc_email_addresses)

    if list_of_cc_email_addresses is None:
        list_of_cc_email_addresses = []
    if list_of_bcc_email_addresses is None:
        list_of_bcc_email_addresses = []

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = '; '.join(list_of_email_addresses)

    if list_of_cc_email_addresses:
        msg['Cc'] = '; '.join(list_of_cc_email_addresses)

    part1 = MIMEText('questo messaggio ha un contenuto html', 'plain')
    part2 = MIMEText(message_body, "html")

    msg.attach(part1)
    msg.attach(part2)

    # Open the files in binary mode and figure out the MIME type
    for file in file_name_list:
        if type(file) is MyTemporaryFile:
            file_name = file.get_file_name()
            data = file.get_content()
        else:
            file_name = os.path.basename(file)

            with open(file, 'rb') as fp:
                data = fp.read()

        ctype, encoding = mimetypes.guess_type(file_name)
        if ctype is None or encoding is not None:
            # If we cannot guess the type or if it's encoded (compressed), use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=file_name)

    syslog.syslog(syslog.LOG_INFO,
                  f"send_simple_html_email2: sending email to '{list_of_email_addresses}' subject='{msg['Subject']}'")

    # Send the email via SMTP server:
    with smtplib.SMTP(EMAIL_HOST) as s:

        total_list = list_of_email_addresses + list_of_cc_email_addresses + list_of_bcc_email_addresses

        # s.login(SENDER_EMAIL, APP_PASSWORD)
        s.sendmail(FROM_EMAIL, total_list, msg.as_string())


def send_email_with_attachment(file_name_list, list_of_email_addresses, subject):
    # Create the container email message.
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(list_of_email_addresses)
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Open the files in binary mode and figure out the MIME type
    for file in file_name_list:
        ctype, encoding = mimetypes.guess_type(file)
        if ctype is None or encoding is not None:
            # If we cannot guess the type or if it's encoded (compressed), use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        with open(file, 'rb') as fp:
            data = fp.read()

        file_name = os.path.basename(file)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=file_name)

    # Send the email via SMTP server:
    with smtplib.SMTP(EMAIL_HOST) as s:
        # Uncomment and set up login if your SMTP server requires authentication
        # s.login(SENDER_EMAIL, APP_PASSWORD)
        s.send_message(msg)


def my_send_email(from_email, to_addresses, subject, body, cc_addresses=None, bcc_addresses=None, attachments=None, email_host=None):
    """
    Send an email with HTML body and optional attachments.

    Parameters:
        subject (str): Email subject.
        body (str): HTML body of the email.
        to_addresses (list): List of recipient email addresses.
        cc_addresses (list, optional): List of CC email addresses.
        bcc_addresses (list, optional): List of BCC email addresses.
        attachments (list, optional): List of attachments (file paths or MyTemporaryFile instances).
        from_email (str, optional): Sender email address.
        email_host (str, optional): SMTP server host.
    """

    if cc_addresses is None:
        cc_addresses = []
    if bcc_addresses is None:
        bcc_addresses = []
    if attachments is None:
        attachments = []

    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_addresses)
    if cc_addresses:
        msg['Cc'] = ', '.join(cc_addresses)

    # Attach body
    msg.set_content("This is a fallback plain text message.")
    msg.add_alternative(body, subtype='html')

    # Attach files
    for attachment in attachments:
        if isinstance(attachment, MyTemporaryFile):
            filename = attachment.get_file_name()
            data = attachment.get_content().encode()
            ctype, _ = mimetypes.guess_type(filename)
        else:
            filename = os.path.basename(attachment)
            ctype, _ = mimetypes.guess_type(attachment)
            with open(attachment, 'rb') as f:
                data = f.read()

        if ctype is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    # Send email
    with smtplib.SMTP(email_host) as s:
        s.send_message(msg, from_addr=from_email, to_addrs=to_addresses + cc_addresses + bcc_addresses)

# Example usage:
# send_email(
#     subject="Your Subject Here",
#     body="<h1>Hello World</h1>",
#     to_addresses=["to@example.com"],
#     cc_addresses=["cc@example.com"],
#     bcc_addresses=["bcc@example.com"],
#     attachments=["/path/to/file.pdf"],
#     from_email="from@example.com",
#     email_host="smtp.example.com"
# )