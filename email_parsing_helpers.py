"""
Module that provides helpers for getting messy, noisy email
content into a format that can be read by standard MIME parsers.
"""

import os
import re

_end_of_simple_header_pattern = re.compile('Content-Length: \d+', re.MULTILINE)
_end_of_multipart_header_pattern = re.compile('X-OriginalArrivalTime: .+\r\n\r\n', re.MULTILINE)

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
