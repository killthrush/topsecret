from email.parser import Parser
import xml.etree.ElementTree as ET
import os
import re
import codecs

process_directory = './email project/temp_processed'
junk_line_pattern = re.compile('^(\.|\s+)$')
end_of_simple_header_pattern = re.compile('Content-Length: \d+', re.MULTILINE)
end_of_multipart_header_pattern = re.compile('X-OriginalArrivalTime: .+\r\n\r\n', re.MULTILINE)


header_list = [
    'Bcc',
    'Comment',
    'Content-Length',
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

def is_start_of_junk_section(text):
    if text == '_________________________________________________________________':
        return True
    if text == '-----Original Message-----':
        return True
    if text == '---------------------------------':
        return True
    return False


def fix_broken_hotmail_headers(text):
    end_of_header_match = end_of_simple_header_pattern.search(text)
    temp_header_text = text[:end_of_header_match.end()].strip()
    lines = temp_header_text.splitlines()[1:]  # first line is not a header...
    fixed_header_lines = reduce(merge_broken_header_lines, lines, [])
    return_text = os.linesep.join(fixed_header_lines) + text[end_of_header_match.end():]
    return return_text


def fix_broken_yahoo_headers(text):
    end_of_header_match = end_of_multipart_header_pattern.search(text)
    temp_header_text = text[:end_of_header_match.end()].strip()
    lines = temp_header_text.splitlines()
    fixed_header_lines = reduce(merge_broken_header_lines, lines, [])
    return_text = os.linesep.join(fixed_header_lines) + '\r\n\r\n' + text[end_of_header_match.end():]
    return return_text


def merge_broken_header_lines(accumulator, item):
    cleaned_item = item.strip()
    for header in header_list:
        if item.startswith(header):
            accumulator.append(cleaned_item)
            return accumulator
    try:
        accumulator[len(accumulator)-1] = accumulator[len(accumulator)-1] + ' ' + cleaned_item
    except IndexError: # edge case where the first line doesn't start with a header
        accumulator.append(cleaned_item)
    return accumulator


def process_email_xml(filename, suffix, parse_email=False):
    tree = ET.parse(filename)
    root = tree.getroot()
    for messageNode in root.iter('message'):
        print messageNode.attrib
        file_name = messageNode.attrib['id'].zfill(4) + '_' + suffix + '.txt'
        with open(os.path.join(process_directory, file_name), "w") as text_file:
            text = messageNode.find('text').text.encode('utf8')
            text = str.lstrip(text, '>') # remove leading char that got into the text somehow

            if parse_email:
                text = fix_broken_hotmail_headers(text)
                parser = Parser()
                message = parser.parsestr(text)
                if not message.is_multipart():
                    text = message.get_payload().strip()
                else:
                    # get image
                    text = message.get_payload(0).get_payload().strip()

            ignore_lines = False
            lines = text.splitlines()
            for line in lines:
                if is_start_of_junk_section(line):
                    ignore_lines = True
                if False:
                    ignore_lines = False
                if not ignore_lines and not junk_line_pattern.match(line):
                    text_file.write(line + '\n')
    # remove original messages


def process_multipart_eml(file_name, counter):

    print file_name
    with open(file_name, 'r') as text_file:
        text = ''.join(text_file.readlines())
        text = fix_broken_yahoo_headers(text)
        parser = Parser()
        message = parser.parsestr(text)
        text = get_nested_payload2(message)
        ignore_lines = False
        lines = text.splitlines()

        file_name = '_' + str(counter) + '_mary.txt'
        with open(os.path.join(process_directory, file_name), 'w') as text_file:
            for line in lines:
                if is_start_of_junk_section(line):
                    ignore_lines = True
                if False:
                    ignore_lines = False
                if not ignore_lines and not junk_line_pattern.match(line):
                    text_file.write(line + '\n')


def process_eml_directory(path, counter):
    for file_name in os.listdir(path):
        process_multipart_eml(os.path.join(path, file_name), counter)
        counter += 1


def get_nested_payload2(message):
    for sub_message in message.walk():
        content_type = sub_message.get_content_type()
        disposition = sub_message.get('Content-Disposition')
        if content_type == 'text/plain' and disposition == None:
            return sub_message.get_payload()
    return None


# TODO: make a flattened list of all the leaf nodes so we can get images and documents
# This currently only finds the first text message
def get_nested_payload(message):

    text = None
    #if not message.is_multipart():
    if not 'multipart/alternative' in message.get_content_type():
        if 'text/plain' in message.get('Content-Type'):
            text = message.get_payload().strip()
    else:
        for next_message in message.get_payload():
            temp = get_nested_payload(next_message)
            if temp:
                text = temp
                break
    return text


def process_all():
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)
    #process_email_xml('./email project/asimov/email_new/from_ben.xml', 'ben', parse_email=True)
    #process_email_xml('./email project/asimov/email_new/from_mary.xml', 'mary')
    counter = 10000
    process_eml_directory('./email project/asimov/emails_mary/2/Mary/', counter)


if __name__ == '__main__':
    process_all()
