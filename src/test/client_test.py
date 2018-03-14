import unittest
import httpretty

from client import https_login, HTTPS_URI


class TestClient(unittest.TestCase):

    @httpretty.activate
    def test_send_data(self):
        httpretty.register_uri(httpretty.POST, HTTPS_URI,
                               body="Data sent to platform")
        result = https_login()
        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
