"""
Email utilities to avoid import conflicts
"""

import smtplib
from email.mime.text import MimeText as EmailMimeText
from email.mime.multipart import MimeMultipart as EmailMimeMultipart
from email.mime.base import MimeBase as EmailMimeBase

# Re-export with clear names
MimeText = EmailMimeText
MimeMultipart = EmailMimeMultipart
MimeBase = EmailMimeBase