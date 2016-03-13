import os
from pymongo import MongoClient
from eml_directory_processor import EMLDirectoryProcessor
from xml_dump_processor import XMLDumpProcessor

process_directory = './email project/temp_processed'


def process_email_xml_dumps():

    processor = XMLDumpProcessor('./email project/asimov/email_new/from_ben.xml', True)
    processor.add_callback("logger", email_message_extracted_handler)
    messages = processor.process()
    counter = 0
    for message in messages:
        file_name = '_' + str(counter) + '_ben.txt'
        with open(os.path.join(process_directory, file_name), "w") as text_file:
            text_file.write(message.get_body())
        print str.format("Wrote file '{0}'.", file_name)
        counter += 1

    processor = XMLDumpProcessor('./email project/asimov/email_new/from_mary.xml')
    processor.add_callback("logger", email_message_extracted_handler)
    messages = processor.process()
    counter = 4000
    for message in messages:
        file_name = '_' + str(counter) + '_mary.txt'
        with open(os.path.join(process_directory, file_name), "w") as text_file:
            text_file.write(message.get_body())
        print str.format("Wrote file '{0}'.", file_name)
        counter += 1


def process_eml_directories():
    processor = EMLDirectoryProcessor('./email project/asimov/emails_mary/2/Mary/')
    processor.add_callback("logger", email_message_extracted_handler)
    messages = processor.process()
    counter = 10000
    for message in messages:
        file_name = '_' + str(counter) + '_mary.txt'
        with open(os.path.join(process_directory, file_name), 'w') as text_file:
            text_file.write(message.get_body())
        print str.format("Wrote file '{0}'.", file_name)
        counter += 1


def process_all():
    if not os.path.exists(process_directory):
        os.makedirs(process_directory)
    process_email_xml_dumps()
    process_eml_directories()


def email_message_extracted_handler(message):
    print str.format("Processed Message")


if __name__ == '__main__':
    process_all()
