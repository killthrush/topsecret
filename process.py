from email.parser import Parser
import xml.etree.ElementTree as ET
import os
import re

process_directory = './email project/temp_processed'
junk_line_pattern = re.compile('^(\.|\s+)$')
end_of_header_pattern = re.compile('Content-Length: \d+', re.MULTILINE)

header_list = [
    'X-RocketMail',
    'X-RocketUID',
    'X-RocketMIF',
    'X-Apparently-To',
    'X-RocketRCL',
    'X-Rocket-Track',
    'Return-Path',
    'Received',
    'X-Originating-IP',
    'X-Originating-Email',
    'From',
    'To',
    'Bcc',
    'Subject',
    'Date',
    'Mime-Version',
    'Content-Type',
    'Message-ID',
    'X-OriginalArrivalTime',
    'Content-Length'
]


def is_start_of_junk_section(text):
    if text == '_________________________________________________________________':
        return True
    if text == '-----Original Message-----':
        return True
    return False


def fix_broken_headers(text):
    end_of_header_match = end_of_header_pattern.search(text)
    temp_header_text = text[:end_of_header_match.end()].strip()
    lines = temp_header_text.splitlines()[1:]  # first line is not a header...
    fixed_header_lines = reduce(merge_broken_header_lines, lines, [])
    return_text = os.linesep.join(fixed_header_lines) + text[end_of_header_match.end():]
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
                text = fix_broken_headers(text)
                parser = Parser()
                message = parser.parsestr(text)
                if not message.is_multipart():
                    text = message.get_payload().strip()
                else:
                    text = message.get_payload(0).get_payload().strip()

            ignoreLines = False
            lines = text.splitlines()
            for line in lines:
                if is_start_of_junk_section(line):
                    ignoreLines = True
                if False:
                    ignoreLines = False
                if not ignoreLines and not junk_line_pattern.match(line):
                    text_file.write(line + '\n')
    # remove original messages


def process_all():
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)
    process_email_xml('./email project/asimov/email_new/from_ben.xml', 'ben', parse_email=True)
    process_email_xml('./email project/asimov/email_new/from_mary.xml', 'mary')


if __name__ == '__main__':
    process_all()
