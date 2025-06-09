from qgis.core import QgsProcessingProvider

from .shape import (
    facade_ratio,
    fractal_dimension,
    square_compactness,
    form_factor,
    circular_compactness,
    convexity,
    rectangularity,
    corners,
)

class MomeQProvider(QgsProcessingProvider):
    """ The """
    def id(self) -> str:
        """ The id of the plugin used for identifying the provider. """
        return 'momeq'
    
    def name(self) -> str:
        """ Human friendly name of the plugin in Processing. """
        return self.tr('momeQ')
    
    def getAlgorithms(self):
        algorithms = [
            facade_ratio(),
            fractal_dimension(),
            square_compactness(),
            form_factor(),
            circular_compactness(),
            convexity(),
            rectangularity(),
            corners(),
            facade_ratio_gpd_new(),
            facade_ratio_gpd_old(),
        ]
        return algorithms
    
    def loadAlgorithms(self):
        """ Load each algorithm into current provider. """
        self.algorithms = self.getAlgorithms()
        for a in self.algorithms:
            self.addAlgorithm(a)