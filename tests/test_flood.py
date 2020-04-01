import unittest
from apps import flood


class TestFlood(unittest.TestCase):
    def test_update_plot(self):
        flood.update_plot()

    def test_update_plot_with_green_areas(self):
        flood.update_plot(green=True)

    def test_update_plot_with_buildings(self):
        flood.update_plot(build=True)

    def test_update_plot_with_density(self):
        flood.update_plot(dens=True)