"""
Module that manages processing an XML extract of an outlook mailbox
into structured EmailMessage instances.
"""

import os
from StringIO import StringIO
from dateutil.parser import parse
import xml.etree.ElementTree as ElementTree
from email.parser import Parser
from common.email_message import EmailMessage
from email_parsing_helpers import (
    fix_broken_hotmail_headers,
    get_nested_payload,
    use_full_parser,
    normalize_to_utc,
    clean_sender,
    clean_recipient
)


class XMLDumpProcessor:
    """
    Class that manages processing an XML extract of an outlook mailbox
    into structured EmailMessage instances.
    """

    def __init__(self, process_path, timezone):
        """
        Initializer for the XMLDumpProcessor class
        :param process_path: Path at which we will find an XML dump file to process
        :param timezone: pytz timezone string used to convert dates to UTC
        :return: None
        """
        self._callbacks = dict()
        self._process_path = process_path
        self._timezone = timezone
        if not os.path.exists(self._process_path):
            raise ValueError(str.format("File '{0}' does not exist.", self._process_path))

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
        Processes XML file content found in the instance's processing path.
        :return: A list of EmailMessage objects parsed from the directory contents
        """
        output_contents = []
        tree = ElementTree.parse(self._process_path)
        root = tree.getroot()
        for messageNode in root.iter('message'):
            message = self._process_single_node(messageNode)
            output_contents.append(message)
            for callback in self._callbacks.values():
                callback(message)
        return output_contents

    def _process_single_node(self, node):
        """
        Extract the contents of a single XML dump node
        :param node: The XML node corresponding to a message
        :return: An EmailMessage instance containing the message contents
        """
        text = unicode(node.find('text').text)
        text = unicode.lstrip(text, u'>')  # remove leading char that got into the text somehow
        if use_full_parser(text):
            text = fix_broken_hotmail_headers(text)
            parser = Parser()
            mime_message = parser.parse(StringIO(text))
            return_message = get_nested_payload(mime_message)
        else:
            return_message = EmailMessage()
            subject_node = node.find('subject')
            from_node = node.find('from')
            to_node = node.find('to')
            date_node = node.find('receivedat')
            subject = unicode(subject_node.text, 'utf-8') if subject_node is not None else ''
            sender = clean_sender('{} <{}>'.format(from_node.find('name').text, from_node.find('email').text))
            recipient = clean_recipient('{} <{}>'.format(to_node.find('name').text, to_node.find('email').text))
            date_string = '{} {}'.format(date_node.find('date').text, date_node.find('time').text)
            return_message.append_body(unicode(text))
            return_message.subject = subject
            return_message.sender = sender
            return_message.recipient = recipient
            return_message.date = parse(date_string)
            return_message.date = normalize_to_utc(return_message.date, self._timezone)
        return_message.source = "XML File {} node {}".format(self._process_path, node.attrib)
        return return_message
