# Import smtplib for the actual sending function
import os
import smtplib

# And imghdr to find the types of our images
# import imghdr
import syslog

# Here are the email package modules we'll need
from email.message import EmailMessage

from colorama import Fore

from mediamatrixhub.settings import DEBUG, FROM_EMAIL, EMAIL_HOST, DEBUG_EMAIL


def send_simple_email(list_of_email_addresses, subject, message_body):
    #  https://docs.python.org/3/library/email.examples.html

    if DEBUG:
        print(f"{Fore.YELLOW}send_simple_email: DEBUG is set, skipping{Fore.RESET}")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(list_of_email_addresses)
    msg.set_content(message_body)

    # Send the email via SMTP server:
    with smtplib.SMTP(EMAIL_HOST) as s:
        # s.login(SENDER_EMAIL, APP_PASSWORD)
        s.send_message(msg)


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

    syslog.syslog(syslog.LOG_INFO, f"send_simple_html_email: sending email to '{list_of_email_addresses}' subject='{msg['Subject']}'" )

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


def send_email_with_attachment(file_name_list, list_of_email_addresses, subject):
    # Create the container email message.
    msg = EmailMessage()
    msg['Subject'] = subject
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(list_of_email_addresses)
    msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Open the files in binary mode.  Use imghdr to figure out the
    # MIME subtype for each specific image.
    for file in file_name_list:
        with open(file, 'rb') as fp:
            data = fp.read()

        file_name = os.path.basename(file)
        msg.add_attachment(data, maintype="application", subtype="xlsx", filename=file_name)

    # Send the email via SMTP server:
    with smtplib.SMTP(EMAIL_HOST) as s:
        # s.login(SENDER_EMAIL, APP_PASSWORD)
        s.send_message(msg)



