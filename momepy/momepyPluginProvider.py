from qgis.core import QgsApplication
from .momepyProvider import MomepyProvider


class MomepyPluginProvider:
    def __init__(self):
        self.provider = MomepyProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
