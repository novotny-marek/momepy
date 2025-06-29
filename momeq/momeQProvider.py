from qgis.core import QgsProcessingProvider

from .shape import (
    FacadeRatio,
    FractalDimension,
    SquareCompactness,
    FormFactor,
    CircularCompactness,
    Convexity,
    Rectangularity,
    Corners,
    ShapeIndex,
    CourtyardIndex,
    Squareness,
    Linearity,
)
from .dimension import (
    CourtyardArea,
    LongestAxisLength,
    StreetProfile,
)


class MomeQProvider(QgsProcessingProvider):
    """The"""

    def id(self) -> str:
        """The id of the plugin used for identifying the provider."""
        return "momeq"

    def name(self) -> str:
        """Human friendly name of the plugin in Processing."""
        return self.tr("momeQ")

    def getAlgorithms(self):
        algorithms = [
            FacadeRatio(),
            FractalDimension(),
            SquareCompactness(),
            FormFactor(),
            CircularCompactness(),
            Convexity(),
            Rectangularity(),
            Corners(),
            ShapeIndex(),
            CourtyardIndex(),
            CourtyardArea(),
            LongestAxisLength(),
            StreetProfile(),
            Squareness(),
            Linearity(),
        ]
        return algorithms

    def loadAlgorithms(self):
        """Load each algorithm into current provider."""
        self.algorithms = self.getAlgorithms()
        for a in self.algorithms:
            self.addAlgorithm(a)
