import os
from pymongo import MongoClient
from eml_directory_processor import EMLDirectoryProcessor
from xml_dump_processor import XMLDumpProcessor

process_directory = './email project/temp_processed'


def process_email_xml_dump(path, parse_email):
    processor = XMLDumpProcessor(path, parse_email)
    processor.add_callback("logger", email_message_extracted_handler)
    messages = processor.process()
    return messages


def process_eml_directory(path):
    processor = EMLDirectoryProcessor(path)
    processor.add_callback("logger", email_message_extracted_handler)
    messages = processor.process()
    return messages


def write_messages_to_files(messages, start_index, sender_tag):
    counter = start_index
    for message in messages:
        file_name = '{}_{}.txt'.format(str(counter).zfill(4), sender_tag)
        with open(os.path.join(process_directory, file_name), 'w') as text_file:
            text_file.write(message.get_body())
        print "Wrote file '{0}'.".format(file_name)
        counter += 1


def process_all():
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)
    all_messages = []
    all_messages += process_email_xml_dump('./email project/asimov/email_new/from_ben.xml', True)
    all_messages += process_email_xml_dump('./email project/asimov/email_new/from_mary.xml', False)
    all_messages += process_eml_directory('./email project/asimov/emails_mary/2/Mary/')
    write_messages_to_files(all_messages, 0, 'a')


def email_message_extracted_handler(message):
    print str.format("Processed Message")


if __name__ == '__main__':
    process_all()
