from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage
from azure.communication.email import (
    EmailClient,
    EmailContent,
    EmailRecipients,
    EmailAddress,
)
from django.conf import settings


class AzureEmailBackend(BaseEmailBackend):
    """
    Custom Django EmailBackend using Azure ACS.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        connection_string = getattr(settings, "AZURE_EMAIL_CONNECTION_STRING", None)
        if not connection_string:
            raise ValueError("AZURE_EMAIL_CONNECTION_STRING not found")
        self.client = EmailClient.from_connection_string(connection_string)
        self.sender = getattr(settings, "AZURE_EMAIL_SENDER", None)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.
        """
        sent_count = 0
        for message in email_messages:
            if self._send(message):
                sent_count += 1
        return sent_count

    def _send(self, email_message: EmailMessage):
        """
        Convert Django EmailMessage to ACS Email and send it.
        """
        if not email_message.recipients():
            return False

        try:
            recipients = {
                "to": [EmailAddress(address=addr) for addr in email_message.to],
            }
            if email_message.cc:
                recipients["cc"] = [
                    EmailAddress(address=addr) for addr in email_message.cc
                ]
            if email_message.bcc:
                recipients["bcc"] = [
                    EmailAddress(address=addr) for addr in email_message.bcc
                ]

            content = EmailContent(
                subject=email_message.subject,
                plain_text=email_message.body,
            )

            message = {
                "senderAddress": self.sender,
                "recipients": EmailRecipients(**recipients),
                "content": content,
            }

            poller = self.client.begin_send(message)
            result = poller.result()

            # Check if ACS accepted the email
            if result:
                return True
        except Exception as e:
            if not self.fail_silently:
                raise
        return False
