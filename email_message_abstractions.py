"""
Module containing email message classes useful for storing
and processing. Abstracts away many of the gory details of
MIME including headers and routing.
"""

import re
import hashlib
import json
from datetime import datetime

_junk_line_pattern = re.compile('^(\.|\s+)$')


class Attachment:
    """
    Encapsulates an abstraction of an email attachment that's useful
    for processing and storage
    """
    def __init__(self, content, content_type, filename=None):
        """
        Initializer for the Attachment class
        :return: None
        """
        self.filename = filename
        self.content_type = content_type
        self.base64_content = content

    def to_dict(self):
        """
        Returns a dict representation of the attachment
        :return: dict
        """
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'content': self.base64_content
        }


class EmailMessage:
    """
    Encapsulates an abstraction of an email message that's useful
    for processing and storage
    """
    def __init__(self):
        """
        Initializer for the EmailMessage class
        :return: None
        """
        self.recipient = None
        self.sender = None
        self.date = None
        self.body = u''
        self.subject = u''
        self.attachments = []
        self.content_hash = None
        self.hasher = hashlib.md5()

    def to_dict(self):
        """
        Returns a dict representation of the email message
        :return: dict
        """
        return_dict = {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': self.subject,
            'date': datetime.isoformat(self.date),
            'body': self.body,
            'attachments': [a.to_dict() for a in self.attachments]
        }
        md5 = hashlib.md5()
        md5.update(json.dumps(return_dict))
        return_dict['content_hash'] = md5.hexdigest()
        return return_dict

    def append_body(self, input_body_text):
        """
        Removes junk from email message body text and appends it to the current body.
        :param input_body_text: The body text to process
        :return: None
        """
        body_accumulator = []
        ignore_lines = False
        lines = input_body_text.splitlines()
        for line in lines:
            if self._is_start_of_junk_section(line):
                ignore_lines = True
            if not ignore_lines:
                body_accumulator.append(line)
        self.body += '\n'.join(body_accumulator)

    def add_attachment(self, content, content_type, filename=None):
        """
        Adds an attachment
        :param content: base64 content for the attachment
        :param content_type: the MIME type of the attachment
        :param filename: the original filename of the attachment
        :return: None
        """
        self.attachments.append(Attachment(content, content_type, filename=filename))

    @staticmethod
    def _is_start_of_junk_section(text):
        """
        Given a line of text from an email, determine whether it's the start of one of
        those annoying ad footers that hotmail and yahoo like to append to the content.
        This allows us to strip out this stuff from the message.
        :param text: A line of text that will be evaluated to see if it's junk
        :return: True if the line is evaluated as junk, else false
        """
        if text == '_________________________________________________________________':
            return True
        if text == '-----Original Message-----':
            return True
        if text == '---------------------------------':
            return True
        if text == '__________________________________________________':
            return True
        if text == '__________________________________':
            return True
        if text == 'Do You Yahoo!?':
            return True
        if text == 'Do you Yahoo!?':
            return True
        return False
