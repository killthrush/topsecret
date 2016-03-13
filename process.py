from pymongo import MongoClient
from email.parser import Parser
import xml.etree.ElementTree as ET
import os
from email_message_abstractions import EmailMessage
from email_parsing_helpers import (
    fix_broken_hotmail_headers,
    fix_broken_yahoo_headers,
    get_nested_payload
)

process_directory = './email project/temp_processed'


def process_email_xml(filename, suffix, parse_email=False):
    tree = ET.parse(filename)
    root = tree.getroot()
    for messageNode in root.iter('message'):
        print messageNode.attrib
        text = messageNode.find('text').text.encode('utf8')
        text = str.lstrip(text, '>') # remove leading char that got into the text somehow

        text_array = [text]
        if parse_email:
            text = fix_broken_hotmail_headers(text)
            parser = Parser()
            mime_message = parser.parsestr(text)
            text_array, attachments = get_nested_payload(mime_message)

        message = EmailMessage()
        for text in text_array:
            message.append_body(text)

        file_name = messageNode.attrib['id'].zfill(4) + '_' + suffix + '.txt'
        with open(os.path.join(process_directory, file_name), "w") as text_file:
            text_file.write(message.get_body())


def process_multipart_eml(file_name, counter):
    print file_name
    with open(file_name, 'r') as text_file:
        text = ''.join(text_file.readlines())
        text = fix_broken_yahoo_headers(text)
        parser = Parser()
        mime_message = parser.parsestr(text)
        text_array, attachments = get_nested_payload(mime_message)

        message = EmailMessage()
        for text in text_array:
            message.append_body(text)

        file_name = '_' + str(counter) + '_mary.txt'
        with open(os.path.join(process_directory, file_name), 'w') as text_file:
            text_file.write(message.get_body())


def process_eml_directory(path, counter):
    for file_name in os.listdir(path):
        if file_name == '.DS_Store':
            continue
        process_multipart_eml(os.path.join(path, file_name), counter)
        counter += 1


def process_all():
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)
    process_email_xml('./email project/asimov/email_new/from_ben.xml', 'ben', parse_email=True)
    process_email_xml('./email project/asimov/email_new/from_mary.xml', 'mary')
    counter = 10000
    process_eml_directory('./email project/asimov/emails_mary/2/Mary/', counter)


if __name__ == '__main__':
    process_all()
