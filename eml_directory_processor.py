"""
Module that manages processing a directory full of .eml
files into structured EmailMessage instances.
"""

import os
from email.parser import Parser
from email_message_abstractions import EmailMessage
from email_parsing_helpers import (
    fix_broken_yahoo_headers,
    get_nested_payload
)


class EMLDirectoryProcessor:
    """
    Class that manages processing a directory full of .eml
    files into structured EmailMessage instances.
    """

    _process_directory = None

    def __init__(self, process_directory):
        """
        Initializer for the EMLDirectoryProcessor class
        :return: None
        """
        self._process_directory = process_directory
        if not os.path.exists(self._process_directory):
            raise ValueError(str.format("Directory '{0}' does not exist.", self._process_directory))

    def process(self):
        """
        Processes EML file content found in the instance's directory..
        :return: A list of EmailMessage objects parsed from the directory contents
        """
        output_contents = []
        for file_name in os.listdir(self._process_directory):
            if file_name == '.DS_Store':
                continue  # Skip these files on OSX systems
            self._process_multipart_eml(os.path.join(self._process_directory, file_name))
        return output_contents

    @staticmethod
    def _process_multipart_eml(file_path):
        """
        Given an EML file, clean it up, parse it, and extract
        the contents we want to keep.
        :param file_path: The path to the EML file to process
        :return: A structured EmailMessage instance
        """
        print file_path
        message = EmailMessage()
        with open(file_path, 'r') as text_file:
            text = ''.join(text_file.readlines())
            text = fix_broken_yahoo_headers(text)
            parser = Parser()
            mime_message = parser.parsestr(text)
            text_array, attachments = get_nested_payload(mime_message)
            for text in text_array:
                message.append_body(text)
        return message
