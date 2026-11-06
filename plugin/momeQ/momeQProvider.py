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
    Elongation,
    EquivalentRectangularIndex,
    CentroidCornerDistance,
    CompactnessWeightedAxis,
    # SunlightOptimised,
)
from .dimension import (
    CourtyardArea,
    FloorArea,
    LongestAxisLength,
    PerimeterWall,
    StreetProfile,
    Volume,
)
from .distribution import (
    Orientation,
    SharedWalls,
    CellAlignment,
    StreetAlignment,
)
from .elements import (
    BufferedLimit,
    MorphologicalTessellation,
    EnclosedTessellation,
    Enclosures,
    ProximityBands,
    GenerateBlocks,
    GetNearestStreet,
    GetNearestNode,
    GetNetworkRatio,
)
from .graph_construction import (
    BuildContiguity,
    BuildHigherOrder,
    BuildDistanceBand,
    BuildFuzzyContiguity,
    BuildKNN,
    BuildKernel,
    BuildTriangulation,
)


class MomeQProvider(QgsProcessingProvider):

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
            Volume(),
            FloorArea(),
            PerimeterWall(),
            Orientation(),
            SharedWalls(),
            CellAlignment(),
            StreetAlignment(),
            Squareness(),
            Linearity(),
            Elongation(),
            EquivalentRectangularIndex(),
            CentroidCornerDistance(),
            CompactnessWeightedAxis(),
            # SunlightOptimised(),
            BufferedLimit(),
            MorphologicalTessellation(),
            EnclosedTessellation(),
            Enclosures(),
            ProximityBands(),
            GenerateBlocks(),
            GetNearestStreet(),
            GetNearestNode(),
            GetNetworkRatio(),
            # Graph algorithms
            BuildContiguity(),
            BuildHigherOrder(),
            BuildDistanceBand(),
            BuildFuzzyContiguity(),
            BuildKNN(),
            BuildKernel(),
            BuildTriangulation(),
        ]
        return algorithms

    def loadAlgorithms(self):
        """Load each algorithm into current provider."""
        self.algs = self.getAlgorithms()
        for a in self.algs:
            self.addAlgorithm(a)
