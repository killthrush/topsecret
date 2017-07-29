"""
Module that manages processing a directory full of .eml
files into structured EmailMessage instances.
"""

import os
import codecs
from StringIO import StringIO
from email.parser import Parser
from email_parsing_helpers import (
    fix_broken_yahoo_headers,
    get_nested_payload,
    use_full_parser,
    normalize_to_utc,
)


class EMLDirectoryProcessor:
    """
    Class that manages processing a directory full of .eml
    files into structured EmailMessage instances.
    """

    def __init__(self, process_directory, timezone):
        """
        Initializer for the EMLDirectoryProcessor class
        :param process_directory: Directory where EML files will be loaded.
        :param timezone: pytz timezone string used to convert dates to UTC
        :return: None
        """
        self._callbacks = dict()
        self._process_directory = process_directory
        self._timezone = timezone
        if not os.path.exists(self._process_directory):
            raise ValueError(str.format("Directory '{0}' does not exist.", self._process_directory))

    def add_callback(self, name, function):
        """
        Add a callback that will be executed when a message is processed
        :param name: The name of the callback
        :param function: A function that will execute when a message is processed
        :return: None
        """
        self._callbacks[name] = function

    def process(self):
        """
        Processes EML file content found in the instance's directory.
        :return: A list of EmailMessage objects parsed from the directory contents
        """
        output_contents = []
        for file_name in os.listdir(self._process_directory):
            if file_name == '.DS_Store':
                continue  # Skip these files on OSX systems
            message = self._process_multipart_eml(os.path.join(self._process_directory, file_name))
            message.date = normalize_to_utc(message.date, self._timezone)
            output_contents.append(message)
            for callback in self._callbacks.values():
                callback(message)
        return output_contents

    @staticmethod
    def _process_multipart_eml(file_path):
        """
        Given an EML file, clean it up, parse it, and extract
        the contents we want to keep.
        :param file_path: The path to the EML file to process
        :return: A structured EmailMessage instance
        """
        with codecs.open(file_path, 'rb', 'windows-1252') as text_file:
            text = str(''.join(text_file.readlines()))
            if use_full_parser(text):
                text = fix_broken_yahoo_headers(text)
            parser = Parser()
            mime_message = parser.parse(StringIO(text))
            return_message = get_nested_payload(mime_message)
            return_message.source = "EML File {}".format(file_path)
        return return_message
