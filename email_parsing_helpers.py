"""
Module that provides helpers for getting messy, noisy email
content into a format that can be read by standard MIME parsers.
"""

import os
import re

_end_of_simple_header_pattern = re.compile('Content-Length: \d+', re.MULTILINE)
_end_of_multipart_header_pattern = re.compile('X-OriginalArrivalTime: .+\r\n\r\n', re.MULTILINE)

# Known header types that we need to be able to recognize
_header_list = [
    'Bcc',
    'Comment',
    'Content-Length',
    'Content-Transfer-Encoding',
    'Content-Type',
    'Date',
    'DomainKey-Signature',
    'From',
    'In-Reply-To',
    'Message-ID',
    'Mime-Version',
    'MIME-Version',
    'Return-Path',
    'Received',
    'Subject',
    'To',
    'X-Account-Key',
    'X-Apparently-To',
    'X-Message-Info',
    'X-Message-Status',
    'X-Mozilla-Status',
    'X-Mozilla-Status2',
    'X-OriginalArrivalTime',
    'X-Originating-IP',
    'X-Originating-Email',
    'X-RocketMail',
    'X-RocketUID',
    'X-RocketMIF',
    'X-RocketRCL',
    'X-Rocket-Track',
    'X-SID-PRA',
    'X-SID-Result',
    'X-UIDL'
]

# Content types that we never want to keep around permanently
_ignored_content_types = [
    'text/html',
    'message/rfc822',
    'multipart/mixed',
    'multipart/alternative'
]

def fix_broken_hotmail_headers(text):
    """
    Some dumps of hotmail messages introduce weird line breaks into header content,
    making them impossible to parse.  This function will fix this content.
    :param text: The input text containing a raw email message exported from hotmail.
    :return: The corrected email message text.
    """
    end_of_header_match = _end_of_simple_header_pattern.search(text)
    temp_header_text = text[:end_of_header_match.end()].strip()
    lines = temp_header_text.splitlines()[1:]  # first line is not a header...
    fixed_header_lines = reduce(_merge_broken_header_lines, lines, [])
    return_text = os.linesep.join(fixed_header_lines) + text[end_of_header_match.end():]
    return return_text


def fix_broken_yahoo_headers(text):
    """
    Some dumps of yahoo messages introduce weird line breaks into header content,
    making them impossible to parse.  This function will fix this content.
    :param text: The input text containing a raw email message exported from yahoo.
    :return: The corrected email message text.
    """
    end_of_header_match = _end_of_multipart_header_pattern.search(text)
    temp_header_text = text[:end_of_header_match.end()].strip()
    lines = temp_header_text.splitlines()
    fixed_header_lines = reduce(_merge_broken_header_lines, lines, [])
    return_text = os.linesep.join(fixed_header_lines) + '\r\n\r\n' + text[end_of_header_match.end():]
    return return_text


def get_nested_payload(mime_message):
    """
    Returns a list of text content and attachments in a MIME message,
    after filtering out unwanted content. Also handles nested content like forwarded messages.
    :param mime_message: The MIME message to traverse looking for content
    :return: A list of plain-text email bodies and a list of base-64 attachments (if any)
    """
    message_content_array = []
    attachments = []
    for sub_message in mime_message.walk():
        content_type = sub_message.get_content_type()
        disposition = sub_message.get('Content-Disposition')
        if content_type == 'text/plain' and disposition is None:
            message_content_array.append(sub_message.get_payload())
        elif content_type in _ignored_content_types and disposition is None:
            pass # throw away contents we don't want
        else:
            attachments.append(sub_message.get_payload())
    return message_content_array, attachments


def _merge_broken_header_lines(accumulator, item):
    """
    Processing function used to reassemble corrected MIME header lines back into
    a block of text at the beginning of an email message.
    :param accumulator: The array of header lines being incrementally built.
    :param item: The current header item being processed
    :return: The updated accumulator array
    """
    cleaned_item = item.strip()
    for header in _header_list:
        if item.startswith(header):
            accumulator.append(cleaned_item)
            return accumulator
    try:
        accumulator[len(accumulator)-1] = accumulator[len(accumulator)-1] + ' ' + cleaned_item
    except IndexError: # edge case where the first line doesn't start with a header
        accumulator.append(cleaned_item)
    return accumulator
