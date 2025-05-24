from qgis.core import QgsProcessingProvider
from .test_algorithm import (
    test_algorithm,
    facade_ratio,
)

class MomeQProvider(QgsProcessingProvider):
    """ The """
    def loadAlgorithms(self):
        """ Load each algorithm into current provider. """
        self.addAlgorithm(test_algorithm())
        self.addAlgorithm(facade_ratio())

    def id(self) -> str:
        """ The id of the plugin used for identifying the provider. """
        return 'momeq'
    
    def name(self) -> str:
        """ Human friendly name of the plugin in Processing. """
        return self.tr('momeQ')