import os
import codecs
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
    mongo_client = MongoClient("mongodb://localhost:27017")
    collection = mongo_client['topsecret']['email']
    counter = start_index
    for message in messages:
        file_name = '{}_{}.txt'.format(str(counter).zfill(4), message.sender)
        with codecs.open(os.path.join(process_directory, file_name), 'w', encoding='utf-8') as text_file:
            text_sections = [
                'From: {}\n'.format(message.sender),
                'To: {}\n'.format(message.recipient),
                'Date: {}\n\n'.format(message.date),
                'Subject: {}\n\n'.format(message.subject),
                message.body
            ]
            text_buffer = '\n'.join(text_sections)
            text_file.write(text_buffer)
            if len(message.attachments) > 0:
                text_file.write('\n')
                for attachment in message.attachments:
                    text_file.write('Attachment: {}\n'.format(attachment.filename or 'No Filename'))
        print "Wrote file '{0}'.".format(file_name)
        document = message.to_dict()
        result = collection.insert_one(document)
        print "Wrote document '{0} with hash {1}'.".format(result.inserted_id, document['content_hash'])
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
