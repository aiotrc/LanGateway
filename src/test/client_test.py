import unittest
import httpretty

from client import send_data_https, HTTPS_DATA_URI


class TestClient(unittest.TestCase):

    @httpretty.activate
    def test_send_data(self):
        httpretty.register_uri(httpretty.POST, HTTPS_DATA_URI,
                               body="Data sent to platform")
        result = send_data_https()
        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
