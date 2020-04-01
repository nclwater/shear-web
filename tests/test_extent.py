import unittest
from apps import extent


class TestExtent(unittest.TestCase):
    def test_update_plot(self):
        extent.update_plot()

    def test_update_plot_with_green_areas(self):
        extent.update_plot(green=True)

    def test_update_plot_with_buildings(self):
        extent.update_plot(build=True)

    def test_update_plot_with_density(self):
        extent.update_plot(dens=True)