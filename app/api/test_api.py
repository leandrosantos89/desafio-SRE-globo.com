from api import app
import unittest


class TestHomeView(unittest.TestCase):

    def setUp(self):
        app_teste = app.test_client()
        self.response = app_teste.get('/')

    def test_get(self):
        self.assertEqual(200, self.response.status_code)

    def test_html_string_response(self):
        self.assertEqual("OK", self.response.data.decode('utf-8'))

    def test_content_type(self):
        self.assertIn('text/html', self.response.content_type)

class TestTotalView(unittest.TestCase):

    def setUp(self):
        app_teste = app.test_client()
        self.response = app_teste.get('/total')

    def test_get(self):
        self.assertEqual(200, self.response.status_code)

    def test_content_type(self):
        self.assertIn('application/json', self.response.content_type)

class TestVotarView(unittest.TestCase):

    def setUp(self):
        app_teste = app.test_client()
        self.response = app_teste.post('/votar/1')

    def test_post(self):
        self.assertEqual(200, self.response.status_code)

    def test_content_type(self):
        self.assertIn('text/html', self.response.content_type)
    
    def test_fail_vote(self):
        app_teste = app.test_client()
        self.response = app_teste.post('/votar/3')
        self.assertEqual(406, self.response.status_code)

