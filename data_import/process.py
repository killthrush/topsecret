import os
import codecs
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from eml_directory_processor import EMLDirectoryProcessor
from xml_dump_processor import XMLDumpProcessor

TIMEZONES = {
    "ben": "US/Eastern",
    "mary": "Asia/Seoul"
}


class Processor(object):
    def __init__(self, process_directory=None, mongo_uri=None):
        if not process_directory:
            process_directory = './email project/temp_processed'
        if not mongo_uri:
            mongo_uri = "mongodb://localhost:27017"
        self._process_directory = process_directory
        self._overall_counter = 0
        self._document_counter = 0
        self._duplicate_counter = 0
        self._mongo_client = MongoClient(mongo_uri)
        self._email_collection = self._mongo_client['topsecret']['email']
        self._source_collection = self._mongo_client['topsecret']['source']
        self._email_collection.delete_many({})
        self._source_collection.delete_many({})

    def process_email_xml_dump(self, path, timezone):
        processor = XMLDumpProcessor(path, timezone)
        processor.add_callback("logger", self.email_message_extracted_handler)
        messages = processor.process()
        return messages

    def process_eml_directory(self, path, timezone):
        processor = EMLDirectoryProcessor(path, timezone)
        processor.add_callback("logger", self.email_message_extracted_handler)
        messages = processor.process()
        return messages

    def write_messages_to_files(self, messages):
        for message in messages:
            file_name = u'{}_{}.txt'.format(str(message.ordinal_number).zfill(4), message.sender)
            with codecs.open(os.path.join(self._process_directory, file_name), 'w', encoding='utf-8') as text_file:
                text_sections = [
                    u'From: {}\n'.format(message.sender),
                    u'To: {}\n'.format(message.recipient),
                    u'Date: {}\n\n'.format(message.date),
                    u'Subject: {}\n\n'.format(message.subject),
                    message.body
                ]
                text_buffer = '\n'.join(text_sections)
                text_file.write(text_buffer)
                if len(message.attachments) > 0:
                    text_file.write('\n')
                    for attachment in message.attachments:
                        text_file.write('Attachment: {}\n'.format(attachment.filename or 'No Filename'))
            print u"Wrote file '{0}'.".format(file_name)
            self.write_mongo_document(message)

    def process_all(self):
        if not os.path.exists(self._process_directory):
            os.makedirs(self._process_directory)
        all_messages = []
        all_messages += self.process_email_xml_dump('./email project/asimov/email_new/from_ben.xml', 'US/Eastern')
        all_messages += self.process_email_xml_dump('./email project/asimov/email_new/from_mary.xml', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/asimov/emails_mary/2/Mary/', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/asimov/emails_mary/mary00000001/', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/asimov/emails_mary/mary/', 'Asia/Seoul')
        all_messages += self.process_email_xml_dump('./email project/baxter/email_new/Copy of from_ben.xml', 'US/Eastern')
        all_messages += self.process_email_xml_dump('./email project/baxter/email_new/from_ben.xml', 'US/Eastern')
        all_messages += self.process_email_xml_dump('./email project/baxter/email_new/from_mary.xml', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/baxter/emails_mary/2/Mary/', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/baxter/emails_mary/mary00000001/', 'Asia/Seoul')
        all_messages += self.process_eml_directory('./email project/baxter/emails_mary/mary/', 'Asia/Seoul')
        self.write_messages_to_files(all_messages)

    def write_mongo_document(self, message):
        document = message.to_dict()
        document['_id'] = document['content_hash']
        try:
            result = self._email_collection.insert_one(document)
            print "Wrote document '{0} with hash {1}'.".format(result.inserted_id, document['content_hash'])
            self._document_counter += 1
        except DuplicateKeyError:
            print "Document with ID {} already exists".format(document['_id'])
            self._duplicate_counter += 1

    def email_message_extracted_handler(self, message):
        self._overall_counter += 1
        message.ordinal_number = self._overall_counter
        message_source = {
            "number": message.ordinal_number,
            "source": message.source,
            "content_hash": message.content_hash
        }
        self._source_collection.insert_one(message_source)
        print "Processed Message {} from {}".format(message.ordinal_number, message.source)

    def print_stats(self):
        stats = (self._overall_counter, self._document_counter, self._duplicate_counter)
        print "{} messages processed, with {} unique messages found and {} duplicates.".format(*stats)
