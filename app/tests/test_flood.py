import unittest
from apps import flood


class TestFlood(unittest.TestCase):
    def test_update_plot(self):
        flood.create_plot()

    def test_update_plot_with_green_areas(self):
        flood.create_plot(green=True)

    def test_update_plot_with_buildings(self):
        flood.create_plot(build=True)

    def test_update_plot_with_density(self):
        flood.create_plot(dens=True)