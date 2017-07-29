import re
import hashlib
import json
from datetime import datetime
from dateutil import parser
from common.attachment import Attachment

_junk_line_pattern = re.compile('^(\.|\s+)$')


class EmailMessage:
    """
    Encapsulates an abstraction of an email message that's useful
    for processing and storage
    """

    def __init__(self, **kwargs):
        """
        Initializer for the EmailMessage class
        :return: None
        """
        self.attachments = []
        self.ordinal_number = None
        self._date = None
        self.source = None
        self.hasher = hashlib.md5()
        self.from_dict(kwargs)

    @property
    def content_hash(self):
        """
        Calculates an MD5 hash of the current contents of the message object
        :return: string
        """
        content = self._get_content()
        md5 = hashlib.md5()
        md5.update(json.dumps(content).encode('utf-8'))
        return md5.hexdigest()

    def _get_content(self):
        """
        Returns a dict containing a subset of the message's data
        :return: dict
        """
        return {
            u'sender': str(self.sender),
            u'recipient': str(self.recipient),
            u'subject': str(self.subject),
            u'date': str(datetime.isoformat(self.date)),
            u'body': str(self.body),
            u'attachments': [a.to_dict() for a in self.attachments]
        }

    def to_dict(self):
        """
        Returns a dict representation of the email message, including a content hash
        used to de-dupe messages.
        :return: dict
        """
        return_dict = self._get_content()
        return_dict[u'content_hash'] = str(self.content_hash)
        return return_dict

    def from_dict(self, input):
        """
        Initialize the instance from a dict
        :param input: The dict used to populate the instance
        :return: None
        """
        self.recipient = str(input.get('recipient'))
        self.sender = str(input.get('sender'))
        self.date = parser.parse(input.get('date')) if input.get('date') else None
        self.body = str(input.get('body'))
        self.subject = str(input.get('subject'))

    def __eq__(self, other):
        """
        Override for equality
        :param other: Another instance to compare
        :return: True if equal, False otherwise
        """
        return type(self) == type(other) and self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """
        Override for inequality
        :param other: Another instance to compare
        :return: True if not equal, False otherwise
        """
        return type(self) != type(other) or self.to_dict() != other.to_dict()

    @property
    def date(self):
        """
        Getter for the date property
        :return: the stored date value
        """
        return self._date

    @date.setter
    def date(self, value):
        """
        Setter for the date property
        :param value: A value to set - supports strings, datetimes, and None
        :return: None
        """
        if isinstance(value, str):
            self._date = parser.parse(value)
        elif isinstance(value, datetime) or value is None:
            self._date = value
        else:
            raise ValueError("Type {} is not supported.".format(type(value)))

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
        self.body = self.body.strip()

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
