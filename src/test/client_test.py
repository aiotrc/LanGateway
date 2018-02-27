import unittest

from client import send_data_https


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        pass

    def test_send_data(self):
        result = send_data_https()
        self.assertEqual(result.status_code, 200)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
