import unittest
from apps import weather


class TestWeather(unittest.TestCase):

    def test_update_lines(self):
        weather.update_lines({'points': [{'id': ''}]}, '1D', 'rain')

    def test_update_href(self):
        weather.update_href('1H', 'rain')

    def test_serve_static(self):
        with weather.app.server.test_client() as client:
            client.get('/rain/1H')
