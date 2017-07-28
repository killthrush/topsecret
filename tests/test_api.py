import unittest
import json
from web import api
from common.email_message import EmailMessage
from common.config import AppConfig
from mock import patch
from flask import abort


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.data_patcher = patch('web.api.data_facade')
        self.facade = self.data_patcher.start()
        single_message = self.get_sample_message().to_dict()
        self.test_messages = [single_message] * 5
        self.facade.load.return_value = self.test_messages
        self.app = api.app.test_client()

    def tearDown(self):
        self.data_patcher.stop()

    def test_get_single_existing_email_with_valid_id(self):
        message = self.get_sample_message().to_dict()
        self.facade.db.email.find_one_or_404.return_value = message
        response = self.app.get('/emails/123')
        self.assertEquals(response.data, json.dumps(message))

    def test_get_missing_email_with_valid_id(self):
        self.facade.db.email.find_one_or_404.side_effect = lambda x: abort(404)
        response = self.app.get('/emails/123')
        self.assertEquals(404, response.status_code)

    def test_get_page_of_emails(self):
        response = self.app.get('/emails?page=10&page_size=20')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load(page=10, page_size=20)

    def test_get_page_given_no_sort_option(self):
        response = self.app.get('/emails')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load()

    def test_get_page_given_unspecified_sort_option(self):
        response = self.app.get('/emails?sort=')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_a_sort_option(self):
        response = self.app.get('/emails?sort=sender')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load(sort=u'sender')

    def test_get_page_given_no_page_size(self):
        response = self.app.get('/emails')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load()

    def test_get_page_given_unspecified_page_size(self):
        response = self.app.get('/emails?page_size=')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_out_of_range_page_size(self):
        response = self.app.get('/emails?page_size=1001')
        self.assertEquals(400, response.status_code)
        response = self.app.get('/emails?page_size=0')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_bad_page_size(self):
        response = self.app.get('/emails?page_size=aaa')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_unspecified_page_number(self):
        response = self.app.get('/emails?page=')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_out_of_range_page_number(self):
        response = self.app.get('/emails?page=-1')
        self.assertEquals(400, response.status_code)
        response = self.app.get('/emails?page=0')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_bad_page_number(self):
        response = self.app.get('/emails?page=aaa')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_garbage_param(self):
        response = self.app.get('/emails?drop_database=111')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_sender_filter(self):
        response = self.app.get('/emails?sender=foobar')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load(sender=u'foobar')

    def test_get_page_given_unspecified_sender_filter(self):
        response = self.app.get('/emails?sender=')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_recipient_filter(self):
        response = self.app.get('/emails?recipient=foobar')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load(recipient=u'foobar')

    def test_get_page_given_unspecified_recipient_filter(self):
        response = self.app.get('/emails?recipient=')
        self.assertEquals(400, response.status_code)

    def test_get_page_given_body_filter(self):
        response = self.app.get('/emails?body=foobar')
        self.assertEquals(200, response.status_code)
        self.assertEquals(json.dumps(self.test_messages), response.get_data())
        self.assert_data_load(body=u'foobar')

    def test_get_page_given_unspecified_body_filter(self):
        response = self.app.get('/emails?body=')
        self.assertEquals(400, response.status_code)

    def get_sample_message(self):
        return EmailMessage(**{
            u'sender': u"me",
            u'recipient': u"you",
            u'subject': u"re:",
            u'date': u"2003-07-31T06:44:38-04:00",
            u'body': u"stuff thaangs"
        })

    def assert_data_load(self, page=1, page_size=10, **kwargs):
        self.facade.load.assert_called_once_with(AppConfig.email_collection, page=page, page_size=page_size, **kwargs)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    user_tests = loader.loadTestsFromTestCase(ApiTests)
    suite = unittest.TestSuite(user_tests)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)
