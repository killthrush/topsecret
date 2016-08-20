#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Module that provides helpers for getting messy, noisy email
content into a format that can be read by standard MIME parsers.
"""

import os
import re
import pytz
from dateutil.parser import parse
from common.email_message import EmailMessage

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

# mappings of cleaned-up senders and recipients (really hard to do unless you're a human)
_recipient_map = {
    None: "",
    "sskeptic@yahoo.com": "Jin Young Kang <sskeptic@yahoo.com>",
    "simitatores@yahoo.com, sskeptic@yahoo.com": "Mary Anne Lee <simitatores@yahoo.com>, Jin Young Kang <sskeptic@yahoo.com>",
    "janjanbinks@yahoo.com, sskeptic@yahoo.com": "Mary Anne Lee <simitatores@yahoo.com>, Stella Dacuma <janjanbinks@yahoo.com>",
    "'jin young kang' <sskeptic@yahoo.com>": "Jin Young Kang <sskeptic@yahoo.com>",
    "\"Jin Young Kang [Sskeptic@Yahoo.Com] (E-mail)\" <sskeptic@yahoo.com>": "Jin Young Kang <sskeptic@yahoo.com>",
    "\"'sskeptic@yahoo.com'\" <sskeptic@yahoo.com>": "Jin Young Kang <sskeptic@yahoo.com>",
    "'jin young kang' <sskeptic@yahoo.com> Cc: \"'bpeterson3@attbi.com'\" <bpeterson3@attbi.com>": "Jin Young Kang <sskeptic@yahoo.com>",
    "simitatores@yahoo.com": "Mary Anne Lee <simitatores@yahoo.com>",
    "<simitatores@yahoo.com>": "Mary Anne Lee <simitatores@yahoo.com>",
    "Ben Peterson <Ben Peterson>": "Ben Peterson <killthrush@hotmail.com>",
    "bpeterson3@attbi.com <bpeterson3@attbi.com>": "Ben Peterson <bpeterson3@attbi.com>",
    "Ben Peterson <killthrush@hotmail.com>": "Ben Peterson <killthrush@hotmail.com>",
    "killthrush@hotmail.com <killthrush@hotmail.com>": "Ben Peterson <killthrush@hotmail.com>",
    "killthrush@hotmail.com": "Ben Peterson <killthrush@hotmail.com>",
    "Ben Peterson": "Ben Peterson <killthrush@hotmail.com>",
    "bpeterson3@attbi.com": "Ben Peterson <bpeterson3@attbi.com>"
}
_sender_map = {
    None: "",
    "\"Ben Peterson\" <killthrush@hotmail.com>": "Ben Peterson <killthrush@hotmail.com>",
    "Ben Peterson <bpeterson3@attbi.com>": "Ben Peterson <bpeterson3@attbi.com>",
    "\"Ben Peterson\" <bpeterson@ariessys.com>": "Ben Peterson <bpeterson@ariessys.com>",
    "jin young kang <SMTP:SSKEPTIC@YAHOO.COM>": "Jin Young Kang <sskeptic@yahoo.com>",
    "mary anne lerma <SMTP:ERGOLITERATI@YAHOO.COM>": "Mary Anne Lerma <ergoliterati@yahoo.com>",
    "sskeptic@yahoo.com <SMTP:SSKEPTIC@YAHOO.COM>": "Jin Young Kang <sskeptic@yahoo.com>",
    "?????????? <SMTP:MIHYUN-_-VV@HANMAIL.NET>": "Mihyun Lee <MIHYUN-_-VV@HANMAIL.NET>",
    "Mary Anne Lee <simitatores@yahoo.com>": "Mary Anne Lee <simitatores@yahoo.com>",
    "mary anne lerma <ergoliterati@yahoo.com>": "Mary Anne Lerma <ergoliterati@yahoo.com>",
    "jin young kang <sskeptic@yahoo.com>": "Jin Young Kang <sskeptic@yahoo.com>",
    "\"jin young kang\" <SMTP:SSKEPTIC@YAHOO.COM>": "Jin Young Kang <sskeptic@yahoo.com>",
    "\"sskeptic@yahoo.com\" <SMTP:SSKEPTIC@YAHOO.COM>": "Jin Young Kang <sskeptic@yahoo.com>",
    "\"¢ß¢Ë¦­Çö¢â\" <SMTP:MIHYUN-_-VV@HANMAIL.NET>": "Mihyun Lee <MIHYUN-_-VV@HANMAIL.NET>",
    "\"mary anne lerma\" <SMTP:ERGOLITERATI@YAHOO.COM>": "Mary Anne Lerma <ergoliterati@yahoo.com>"
}


def clean_sender(sender):
    """
    Clean a sender address by using a predefined map
    :param sender: the sender address string to clean
    :return:
    """
    if sender in _sender_map:
        return _sender_map[sender]
    return ''


def clean_recipient(recipient):
    """
    Clean a recipient address by using a predefined map
    :param recipient: the recipient address string to clean
    :return:
    """
    if recipient in _recipient_map:
        return _recipient_map[recipient]
    return ''


def use_full_parser(text):
    """
    Examine the text to see if we need to use full MIME parsing or not.
    :param text: The text to examine
    :return: Boolean - true if full parsing needs to be used else false
    """
    end_of_header_match = _end_of_simple_header_pattern.search(text)
    return end_of_header_match is not None


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
    Returns a single message object from a list of text content and attachments in a MIME message,
    after filtering out unwanted content. Also handles nested content like forwarded messages.
    :param mime_message: The MIME message to traverse looking for content
    :return: A list of plain-text email bodies and a list of base-64 attachments (if any)
    """
    return_message = EmailMessage()
    return_message.subject = mime_message.get('Subject')
    return_message.sender = clean_sender(mime_message.get('From'))
    return_message.recipient = clean_recipient(mime_message.get('To'))
    return_message.date = parse(mime_message.get('Date'))
    for sub_message in mime_message.walk():
        content_type = sub_message.get_content_type()
        disposition = sub_message.get('Content-Disposition')
        if content_type == 'text/plain' and disposition is None:
            x = unicode(sub_message.get_payload())
            return_message.append_body(x)
        elif content_type in _ignored_content_types and disposition is None:
            pass  # throw away contents we don't want
        else:
            return_message.add_attachment(sub_message.get_payload(), content_type=content_type, filename=disposition)
    return return_message


def normalize_to_utc(date, timezone):
    """
    Coerce an unknown date to the given timezone, then to UTC
    :param date: the date to coerce
    :param timezone: pytz timezone string used to convert dates to UTC
    :return: the input date, coerced to a utc date
    """
    local_tz = pytz.timezone(timezone)
    new_date = date.replace(tzinfo = local_tz)
    utc_tz = pytz.timezone('UTC')
    new_date = new_date.astimezone(utc_tz)
    return new_date


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
    except IndexError:  # edge case where the first line doesn't start with a header
        accumulator.append(cleaned_item)
    return accumulator


