import unittest
from apps import weather
from index import navbar


class TestWeather(unittest.TestCase):
    def test_layout(self):
        weather.layout(navbar)

    def test_update_lines(self):
        weather.update_lines({'points': [{'id': ''}]}, '1D', 'rain')

    def test_update_map(self):
        weather.update_map(0, '1H', 'rain')
