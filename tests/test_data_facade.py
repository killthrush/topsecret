from common.email_message import EmailMessage
from common.data_facade import DataFacade
from common.config import AppConfig
from flask import Flask
import unittest


class DataFacadeTests(unittest.TestCase):
    def setUp(self):
        self.facade = DataFacade()
        self.app = Flask(AppConfig.app_name)
        self.app.config['MONGO_HOST'] = AppConfig.mongo_uri
        self.email_collection = AppConfig.email_collection + '_test'
        self.source_collection = AppConfig.source_collection + '_test'

    def tearDown(self):
        with self.app.app_context():
            if self.facade.is_bound:
                self.facade.clear_collection(self.email_collection)

    def test_store_and_load_from_flask(self):
        with self.app.app_context():
            self.facade.bind_flask(self.app)
            message = EmailMessage(subject='foo', body='bar', sender='baz', recipient='bip', date='2016-07-07')
            self.facade.store(self.email_collection, message.to_dict())
            loaded_messages = self.facade.load(self.email_collection, content_hash=message.content_hash)
            self.assertEqual(1, len(loaded_messages))
            self.assertEqual(message, EmailMessage(**loaded_messages[0]))

    def test_store_and_load_from_pymongo(self):
        self.facade.bind(AppConfig.mongo_uri)
        message = EmailMessage(subject='foo', body='bar', sender='baz', recipient='bip', date='2016-07-07')
        self.facade.store(self.email_collection, message.to_dict())
        loaded_messages = self.facade.load(self.email_collection, content_hash=unicode(message.content_hash))
        self.assertEqual(1, len(loaded_messages))
        self.assertEqual(message, EmailMessage(**loaded_messages[0]))

    def test_store_and_load_a_page(self):
        self.facade.bind(AppConfig.mongo_uri)
        for i in range(1, 1000):
            message = EmailMessage(subject='foo{}'.format(i), body='bar', sender='baz', recipient='bip', date='2016-07-07')
            self.facade.store(self.email_collection, message.to_dict())
        loaded_messages = self.facade.load(self.email_collection, page=12, page_size=6)
        self.assertEqual(6, len(loaded_messages))
        for num, email in zip(range(67, 72), [EmailMessage(**message) for message in loaded_messages]):
            self.assertEqual(email.subject, 'foo{}'.format(num))

    def test_filter_by_field(self):
        self.facade.bind(AppConfig.mongo_uri)
        for i in range(1, 100):
            message = EmailMessage(subject='foo{}foo'.format(i), body='bar', sender='baz', recipient='bip', date='2016-07-07')
            self.facade.store(self.email_collection, message.to_dict())
        loaded_messages = self.facade.load(self.email_collection, page_size=60, subject='1')
        self.assertEqual(19, len(loaded_messages))
        for email in [EmailMessage(**message) for message in loaded_messages]:
            self.assertTrue('1' in email.subject)

    def test_sorting(self):
        self.facade.bind(AppConfig.mongo_uri)
        test_messages = []
        for i in range(0, 100):
            message = EmailMessage(subject='foo{}foo'.format(i), body='bar', sender='baz', recipient='bip', date='2016-07-07')
            self.facade.store(self.email_collection, message.to_dict())
            test_messages.append(message)
        loaded_messages = self.facade.load(self.email_collection, page_size=100, sort='subject')
        expected_messages = sorted(test_messages, key=lambda m: m.subject)
        self.assertEqual(100, len(loaded_messages))
        self.assertEqual(100, len(expected_messages))
        compare_list = zip(loaded_messages, expected_messages)
        for item in enumerate(compare_list):
            item1 = item[1][0]
            item2 = item[1][1]
            msg = 'Item {} did not match: {} != {}'.format(item[0], item1['subject'], item2.subject)
            self.assertEqual(item1['subject'], item2.subject, msg)

    def test_flask_bound_facade_cannot_rebind(self):
        with self.assertRaises(TypeError):
            with self.app.app_context():
                self.facade.bind_flask(self.app)
                self.facade.bind_flask(self.app)

    def test_pymongo_bound_facade_cannot_rebind(self):
        with self.assertRaises(TypeError):
            self.facade.bind(AppConfig.mongo_uri)
            self.facade.bind(AppConfig.mongo_uri)

    def test_pymongo_bound_facade_cannot_rebind_to_flask(self):
        with self.assertRaises(TypeError):
            with self.app.app_context():
                self.facade.bind(AppConfig.mongo_uri)
                self.facade.bind_flask(self.app)

    def test_flask_bound_facade_cannot_rebind_to_pymongo(self):
        with self.assertRaises(TypeError):
            with self.app.app_context():
                self.facade.bind_flask(self.app)
                self.facade.bind(AppConfig.mongo_uri)

    def test_db_property_from_pymongo(self):
        self.facade.bind(AppConfig.mongo_uri)
        self.assertIsNotNone(self.facade.db)

    def test_db_property_from_flask(self):
        with self.app.app_context():
            self.facade.bind_flask(self.app)
            self.assertIsNotNone(self.facade.db)

    def test_is_bound_property(self):
        with self.app.app_context():
            self.assertFalse(self.facade.is_bound)
            self.facade.bind_flask(self.app)
            self.assertTrue(self.facade.is_bound)

    def test_unbound_facade_raises_exception_on_db_property_access(self):
        with self.assertRaises(ValueError):
            broken_facade = DataFacade()
            broken_facade.db

    def test_unbound_facade_raises_exception_on_load(self):
        with self.assertRaises(ValueError):
            broken_facade = DataFacade()
            broken_facade.load(self.email_collection, foo='bar')

    def test_unbound_facade_raises_exception_on_store(self):
        with self.assertRaises(ValueError):
            broken_facade = DataFacade()
            broken_facade.load(self.email_collection, foo='bar')

    def test_unbound_facade_raises_exception_on_clear_collection(self):
        with self.assertRaises(ValueError):
            broken_facade = DataFacade()
            broken_facade.clear_collection(self.email_collection, foo='bar')

if __name__ == '__main__':
    loader = unittest.TestLoader()
    user_tests = loader.loadTestsFromTestCase(DataFacadeTests)
    suite = unittest.TestSuite(user_tests)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)