import base64
import email
from typing import Optional
from googleapiclient.errors import HttpError
from .gmail_service import get_gmail_service

from langchain_core.tools import tool

@tool
def list_email_labels():
    """
    List all available email labels/folders in the Gmail account.

    Returns:
        str: Formatted list of available labels
    """
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            return "No labels found."

        # Format labels into a readable string
        label_list = "\n".join([
            f"- {label['name']} (ID: {label['id']})"
            for label in labels
        ])

        return f"Available Labels:\n{label_list}"

    except HttpError as error:
        return f"An error occurred while listing labels: {error}"

@tool
def list_recent_emails(label_name: Optional[str] = None, max_results: int = 10):
    """
    List recent emails, optionally filtered by a specific label.

    Args:
        label_name (Optional[str]): Name of the label to filter emails
        max_results (int): Maximum number of emails to retrieve (default 10)

    Returns:
        str: Formatted list of recent emails
    """
    try:
        service = get_gmail_service()

        # Get label ID if a label name is provided
        label_id = None
        if label_name:
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            label_id = next((label['id'] for label in labels if label['name'] == label_name), None)

            if not label_id:
                return f"Label '{label_name}' not found."

        # Prepare query parameters
        query_params = {
            'userId': 'me',
            'maxResults': max_results
        }
        if label_id:
            query_params['labelIds'] = [label_id]

        # Retrieve emails
        results = service.users().messages().list(**query_params).execute()
        messages = results.get('messages', [])

        if not messages:
            return "No emails found."

        # Format email details
        email_details = []
        for i, msg in enumerate(messages, 1):
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message['payload']['headers']

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

            email_details.append(
                f"{i}. From: {sender}\n"
                f"   Subject: {subject}\n"
                f"   Date: {date}\n"
                f"   Message ID: {msg['id']}"
            )

        return "Recent Emails:\n" + "\n\n".join(email_details)

    except HttpError as error:
        return f"An error occurred while listing emails: {error}"

@tool
def read_email_content(message_id: str):
    """
    Retrieve the full content of a specific email.

    Args:
        message_id (str): ID of the email to retrieve

    Returns:
        str: Formatted email content
    """
    try:
        service = get_gmail_service()

        # Get the full message
        message = service.users().messages().get(userId='me', id=message_id).execute()

        # Extract headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

        # Extract body
        def get_body(msg):
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                return base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
            return "No readable content found."

        body = get_body(message)

        return (
            f"Email Details:\n"
            f"From: {sender}\n"
            f"Subject: {subject}\n"
            f"Date: {date}\n\n"
            f"Content:\n{body}"
        )

    except HttpError as error:
        return f"An error occurred while reading email: {error}"

@tool
def send_email(to: str, subject: str, body: str):
    """
    Send a new email.

    Args:
        to (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content

    Returns:
        str: Confirmation or error message
    """
    try:
        service = get_gmail_service()

        # Construct the email message
        message = email.message.EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['Subject'] = subject

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send the message
        send_message = service.users().messages().send(
            userId="me", 
            body={'raw': raw_message}
        ).execute()

        return f"Email sent successfully! Message ID: {send_message['id']}"

    except HttpError as error:
        return f"An error occurred while sending email: {error}"

@tool
def reply_to_email(message_id: str, reply_text: str):
    """
    Reply to a specific email thread.

    Args:
        message_id (str): ID of the original message to reply to
        reply_text (str): Content of the reply

    Returns:
        str: Confirmation or error message
    """
    try:
        service = get_gmail_service()

        # Retrieve the original message
        original_message = service.users().messages().get(userId="me", id=message_id).execute()

        # Extract headers
        headers = original_message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Re: No Subject')
        if not subject.startswith('Re: '):
            subject = f'Re: {subject}'

        # Find the recipient
        to_header = next((h['value'] for h in headers if h['name'] == 'From'), '')

        # Construct the reply message
        message = email.message.EmailMessage()
        message.set_content(reply_text)
        message['To'] = to_header
        message['Subject'] = subject
        message['In-Reply-To'] = message_id
        message['References'] = message_id

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send the message
        send_message = service.users().messages().send(
            userId="me", 
            body={'raw': raw_message}
        ).execute()

        return f"Reply sent successfully! Message ID: {send_message['id']}"

    except HttpError as error:
        return f"An error occurred while replying to email: {error}"
