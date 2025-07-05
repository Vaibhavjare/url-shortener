import unittest
from app import app, get_db
from flask import url_for

class URLShortenerTestCase(unittest.TestCase):

    def setUp(self):
        # Setup test client and database
        self.app = app.test_client()
        self.app.testing = True

        # Make sure test data doesn't affect main DB
        self.db = get_db()
        self.cur = self.db.cursor()
        self.clean_test_entries()

    def clean_test_entries(self):
        # Remove any previous test short_code
        self.cur.execute("DELETE FROM urls WHERE short_code IN ('test123', 'customcode')")
        self.db.commit()

    def tearDown(self):
        # Cleanup after each test
        self.clean_test_entries()
        self.cur.close()
        self.db.close()

    def test_home_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shorten your URL', response.data)

    def test_url_shortening_random(self):
        response = self.app.post('/', data={
            'url': 'https://www.example.com',
            'custom': '',
            'name': 'TestUser'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Short URL:', response.data)

    def test_custom_short_code(self):
        response = self.app.post('/', data={
            'url': 'https://www.testcustom.com',
            'custom': 'customcode',
            'name': 'Vaibhav'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'customcode', response.data)

    def test_redirect_valid_short_code(self):
        # Insert a known short code
        self.cur.execute("INSERT INTO urls (original_url, short_code, name) VALUES (%s, %s, %s)",
                         ("https://www.redirecttest.com", "test123", "Vaibhav"))
        self.db.commit()

        response = self.app.get('/test123', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # 302 = Redirect
        self.assertIn('https://www.redirecttest.com', response.headers['Location'])

    def test_redirect_invalid_short_code(self):
        response = self.app.get('/nonexistent', follow_redirects=False)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
