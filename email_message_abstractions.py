"""
Module containing email message classes useful for storing
and processing. Abstracts away many of the gory details of
MIME including headers and routing.
"""

import re

_junk_line_pattern = re.compile('^(\.|\s+)$')


class Attachment():
    """
    Encapsulates an abstraction of an email attachment that's useful
    for processing and storage
    """
    _fields = dict()

    def __init__(self):
        """
        Initializer for the Attachment class
        :return: None
        """
        self._fields['filename'] = None
        self._fields['content_type'] = None
        self._fields['base64_content'] = None


class EmailMessage():
    """
    Encapsulates an abstraction of an email message that's useful
    for processing and storage
    """
    _fields = dict()

    def __init__(self):
        """
        Initializer for the EmailMessage class
        :return: None
        """
        self._fields['from'] = None
        self._fields['to'] = None
        self._fields['date'] = None
        self._fields['body'] = ''
        self._fields['subject'] = ''
        self._fields['attachments'] = []
        self._fields['content_hash'] = None

    def set_subject(self, subject_text):
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
