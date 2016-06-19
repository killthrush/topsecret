import re
import hashlib
import json
from datetime import datetime
from common.attachment import Attachment

_junk_line_pattern = re.compile('^(\.|\s+)$')


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
        self.ordinal_number = None
        self.source = None
        self.hasher = hashlib.md5()

    @property
    def content_hash(self):
        """
        Calculates an MD5 hash of the current contents of the message object
        :return: string
        """
        content = self._get_content()
        md5 = hashlib.md5()
        md5.update(json.dumps(content))
        return md5.hexdigest()

    def _get_content(self):
        """
        Returns a dict containing a subset of the message's data
        :return: dict
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': self.subject,
            'date': datetime.isoformat(self.date),
            'body': self.body,
            'attachments': [a.to_dict() for a in self.attachments]
        }

    def to_dict(self):
        """
        Returns a dict representation of the email message, including a content hash
        used to de-dupe messages.
        :return: dict
        """
        return_dict = self._get_content()
        return_dict['content_hash'] = self.content_hash
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
        junk_patterns = {
            '_________________________________________________________________',
            '-----Original Message-----',
            '---------------------------------',
            '__________________________________________________',
            '__________________________________',
            'Do You Yahoo!?',
            'Do you Yahoo!?'
        }
        return text in junk_patterns
