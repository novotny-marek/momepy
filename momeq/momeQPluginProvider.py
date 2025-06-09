from qgis.core import QgsApplication
from .momeQProvider import MomeQProvider

class MomeQPluginProvider():
    def __init__(self):
        self.provider = MomeQProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)