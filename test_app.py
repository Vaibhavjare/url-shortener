import unittest
from app import app, get_db

class URLShortenerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.db = get_db()
        self.cur = self.db.cursor()
        self.clean_test_data()

    def clean_test_data(self):
        self.cur.execute("DELETE FROM urls WHERE short_code IN ('test123', 'custom123', 'abc999')")
        self.db.commit()

    def tearDown(self):
        self.clean_test_data()
        self.cur.close()
        self.db.close()

    def test_home_page_loads(self):
        """Test if home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shorten a long URL', response.data)  # Match your HTML <h2> content

    def test_create_short_url(self):
        """Test creating a short URL with required fields"""
        response = self.app.post('/', data={
            'url': 'https://example.com',
            'custom': 'test123',
            'name': 'Vaibhav'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'test123', response.data)

    def test_duplicate_custom_code(self):
        """Test that using the same custom code twice fails"""
        # First insert
        self.cur.execute("INSERT INTO urls (original_url, short_code, name) VALUES (%s, %s, %s)",
                         ("https://abc.com", "abc999", "Vaibhav"))
        self.db.commit()

        # Try to insert again with same code
        response = self.app.post('/', data={
            'url': 'https://xyz.com',
            'custom': 'abc999',
            'name': 'Vaibhav'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already exists', response.data)

    def test_redirect_valid_code(self):
        """Test redirect from short to original URL"""
        self.cur.execute("INSERT INTO urls (original_url, short_code, name) VALUES (%s, %s, %s)",
                         ("https://redirect.com", "custom123", "Vaibhav"))
        self.db.commit()

        response = self.app.get('/custom123', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://redirect.com", response.headers["Location"])

    def test_redirect_invalid_code(self):
        """Test 404 for unknown short code"""
        response = self.app.get('/unknowncode', follow_redirects=False)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
