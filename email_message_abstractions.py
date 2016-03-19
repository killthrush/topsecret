"""
Module containing email message classes useful for storing
and processing. Abstracts away many of the gory details of
MIME including headers and routing.
"""

import re

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
        self._fields = dict()
        self._fields['filename'] = filename
        self._fields['content_type'] = content_type
        self._fields['base64_content'] = content


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
        self._fields = dict()
        self._fields['recipient'] = None
        self._fields['sender'] = None
        self._fields['date'] = None
        self._fields['body'] = u''
        self._fields['subject'] = u''
        self._fields['attachments'] = []
        self._fields['content_hash'] = None

    def get_date(self):
        """
        Returns the current date stored in the message instance
        :return: The date
        """
        return self._fields['date']

    def set_date(self, date):
        """
        Set the message date
        :param date: The date to store
        :return: None
        """
        self._fields['date'] = date

    def get_recipient(self):
        """
        Returns the current recipient stored in the message instance
        :return: The recipient string
        """
        return self._fields['recipient']

    def set_recipient(self, recipient):
        """
        Set the message recipient
        :param recipient: The recipient to store
        :return: None
        """
        self._fields['recipient'] = recipient

    def get_sender(self):
        """
        Returns the current sender stored in the message instance
        :return: The sender string
        """
        return self._fields['sender']

    def set_sender(self, sender):
        """
        Set the message sender
        :param sender: The sender to store
        :return: None
        """
        self._fields['sender'] = sender

    def get_subject(self):
        """
        Returns the current subject stored in the message instance
        :return: The subject string
        """
        return self._fields['subject']

    def set_subject(self, subject_text):
        """
        Set the message subject
        :param subject_text: The subject to store
        :return: None
        """
        self._fields['subject'] = subject_text

    def get_body(self):
        """
        Returns the current body stored in the message instance
        :return: The body string
        """
        return self._fields['body']

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
        self._fields['body'] += '\n'.join(body_accumulator)

    def add_attachment(self, content, content_type, filename=None):
        """
        Adds an attachment
        :param content: base64 content for the attachment
        :param content_type: the MIME type of the attachment
        :param filename: the original filename of the attachment
        :return: None
        """
        self._fields['attachments'].append(Attachment(content, content_type, filename=filename))

    def get_attachments(self):
        """
        Returns the current list of attachments stored in the message instance
        :return: The attachments list
        """
        return self._fields['attachments']

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
