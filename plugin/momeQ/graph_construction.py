"""
Graph construction algorithms for momeQ plugin.

These algorithms wrap libpysal.graph.Graph methods to create spatial graphs
that can be used as inputs for various momepy functions.

Each algorithm outputs a QGIS table (edge list) with the following columns:
- source: Index of the source node
- target: Index of the target node  
- weight: Edge weight (if available, depending on graph type)

These edge list tables can be:
- Used in QGIS processing models
- Exported to various formats
- Loaded in Python and converted to libpysal Graph objects for use with momepy
"""

import os
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsFields,
    QgsProcessingException,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFile,
    QgsProcessingParameterEnum,
)
from PyQt6.QtCore import QMetaType

from .utils import qgs_to_gpd


class GraphAlgorithm(QgsProcessingAlgorithm):
    """Base class for graph construction algorithms."""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def input_geometry_types(self) -> list:
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def input_layer_name(self) -> str:
        return "Input geometry layer"

    def get_additional_parameters(self) -> list:
        """Return additional parameters specific for this algorithm."""
        return []

    def build_graph(self, gdf, parameters, context):
        """Build graph from GeoDataFrame. Must be implemented by subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement build_graph()"
        )

    def initAlgorithm(self, configuration=None):
        """Initialize algorithm with input/output plus additional parameters."""
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.input_layer_name(),
                self.input_geometry_types(),
            )
        )

        # Add algorithm-specific parameters
        for param in self.get_additional_parameters():
            self.addParameter(param)

        # Output is a table (edge list) with source, target, weight
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.displayName()
            )
        )

    def processAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        """Process algorithm to build graph and output edge list."""
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Input validation
        if source is None:
            raise QgsProcessingException("Input layer is required.")

        if source.featureCount() == 0:
            raise QgsProcessingException("Input layer has no features.")

        # Convert to GeoDataFrame/GeoSeries
        # Convert to GeoDataFrame
        # Use FID as index for consistency with momepy
        field_names = [field.name() for field in source.fields()]
        if 'fid' in field_names:
            gdf = qgs_to_gpd(source, attribute_fields=['fid'])
            gdf = gdf.set_index('fid')
        else:
            gdf = qgs_to_gpd(source)

        # Build graph using the specific algorithm implementation
        feedback.pushInfo("Building graph...")
        graph = self.build_graph(gdf, parameters, context)

        # Prepare output fields for edge list
        fields = QgsFields()
        fields.append(QgsField("source", QMetaType.Type.Int))
        fields.append(QgsField("target", QMetaType.Type.Int))
        if hasattr(graph, 'weights') and graph.weights is not None:
            fields.append(QgsField("weight", QMetaType.Type.Double))

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            Qgis.WkbType.NoGeometry,
            source.sourceCrs(),
        )

        # Get edge list from graph
        feedback.pushInfo("Extracting edges...")
        edges = []
        all_indices = list(gdf.index)  # Get all feature indices
        
        if hasattr(graph, 'edges'):
            # Newer libpysal versions
            edges = list(graph.edges)
        elif hasattr(graph, 'neighbors'):
            # Build edge list from neighbors
            neighbors_dict = graph.neighbors
            for i, neighbor_list in neighbors_dict.items():
                for j in neighbor_list:
                    if i < j:  # Avoid duplicates for undirected graphs
                        edges.append((i, j))
        elif hasattr(graph, 'index_pairs'):
            # Use index_pairs if available
            focal, neighbor = graph.index_pairs
            for i, j in zip(focal, neighbor):
                if i != j:  # Skip self-loops
                    edges.append((i, j))

        # Add features to sink
        total = len(edges)
        edge_weights = getattr(graph, 'weights', None)
        
        for idx, (source_idx, target_idx) in enumerate(edges):
            if feedback.isCanceled():
                break

            feature = QgsFeature(fields)
            feature.setAttribute("source", source_idx)
            feature.setAttribute("target", target_idx)
            
            if edge_weights is not None:
                # Get weight for this edge
                weight = edge_weights.get((source_idx, target_idx)) or \
                        edge_weights.get((target_idx, source_idx)) or \
                        1.0
                feature.setAttribute("weight", float(weight))

            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(int((idx / total) * 100))

        feedback.pushInfo("Graph construction complete.")

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class BuildContiguity(GraphAlgorithm):
    """Build contiguity graph from polygon layer."""

    def name(self) -> str:
        return "build_contiguity"

    def displayName(self) -> str:
        return "Build Contiguity Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a spatial contiguity graph from polygon geometries. "
            "Edges represent adjacency (shared boundaries) between polygons. "
            "Output is a table with source, target, and weight columns. "
            "This can be used as input for various momepy functions."
        )

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        return Graph.build_contiguity(gdf)


class BuildHigherOrder(GraphAlgorithm):
    """Build higher-order contiguity graph."""

    ORDER = "ORDER"

    def name(self) -> str:
        return "build_higher_order"

    def displayName(self) -> str:
        return "Build Higher-Order Contiguity Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a higher-order contiguity graph. Higher-order contiguity "
            "connects polygons that are within a specified number of steps "
            "from each other in the original contiguity graph. "
            "Output is a table with source, target, and weight columns."
        )

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterNumber(
                self.ORDER,
                "Order",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=2,
                minValue=1,
            ),
        ]

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        order = self.parameterAsInt(parameters, self.ORDER, context)
        return Graph.build_contiguity(gdf).higher_order(order)


class BuildDistanceBand(GraphAlgorithm):
    """Build distance band graph."""

    THRESHOLD = "THRESHOLD"
    BINARY = "BINARY"
    ALPHA = "ALPHA"

    def name(self) -> str:
        return "build_distance_band"

    def displayName(self) -> str:
        return "Build Distance Band Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a distance band graph. Connects observations within a specified "
            "distance threshold. Can be binary (0/1) or weighted by distance. "
            "Output is a table with source, target, and weight columns."
        )

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                "Distance threshold",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1000.0,
                minValue=0.0,
            ),
            QgsProcessingParameterBoolean(
                self.BINARY,
                "Binary weights",
                defaultValue=True,
            ),
            QgsProcessingParameterNumber(
                self.ALPHA,
                "Distance decay parameter (alpha)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=-1.0,
                optional=True,
            ),
        ]

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        threshold = self.parameterAsDouble(parameters, self.THRESHOLD, context)
        binary = self.parameterAsBool(parameters, self.BINARY, context)
        alpha = self.parameterAsDouble(parameters, self.ALPHA, context)
        # build_distance_band requires Point geometries, so use centroids
        if alpha != -1.0:
            return Graph.build_distance_band(gdf.centroid, threshold, binary=binary, alpha=alpha)
        return Graph.build_distance_band(gdf.centroid, threshold, binary=binary)


class BuildFuzzyContiguity(GraphAlgorithm):
    """Build fuzzy contiguity graph."""

    PERMUTATIONS = "PERMUTATIONS"

    def name(self) -> str:
        return "build_fuzzy_contiguity"

    def displayName(self) -> str:
        return "Build Fuzzy Contiguity Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a fuzzy contiguity graph. Connects polygons based on shared "
            "boundaries with weights based on the length of the shared boundary. "
            "Output is a table with source, target, and weight columns."
        )

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterNumber(
                self.PERMUTATIONS,
                "Number of permutations",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=99,
                minValue=1,
            ),
        ]

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        permutations = self.parameterAsInt(parameters, self.PERMUTATIONS, context)
        return Graph.build_fuzzy_contiguity(gdf, permutations=permutations)


class BuildKNN(GraphAlgorithm):
    """Build k-nearest neighbors graph."""

    K = "K"
    DISTANCE_METRIC = "DISTANCE_METRIC"

    def name(self) -> str:
        return "build_knn"

    def displayName(self) -> str:
        return "Build K-Nearest Neighbors Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a k-nearest neighbors graph. Connects each observation to its "
            "k nearest neighbors based on the specified distance metric. "
            "Output is a table with source, target, and weight columns."
        )

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterNumber(
                self.K,
                "Number of neighbors (k)",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=5,
                minValue=1,
            ),
            QgsProcessingParameterEnum(
                self.DISTANCE_METRIC,
                "Distance metric",
                options=["euclidean", "manhattan", "arc", "great_circle"],
                defaultValue=0,  # euclidean
            ),
        ]

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        k = self.parameterAsInt(parameters, self.K, context)
        distance_metric_idx = self.parameterAsInt(parameters, self.DISTANCE_METRIC, context)
        distance_metric = ["euclidean", "manhattan", "arc", "great_circle"][distance_metric_idx]
        # build_knn requires Point geometries, so use centroids
        return Graph.build_knn(gdf.centroid, k=k, metric=distance_metric)


class BuildKernel(GraphAlgorithm):
    """Build kernel distance graph."""

    BANDWIDTH = "BANDWIDTH"
    KERNEL = "KERNEL"

    def name(self) -> str:
        return "build_kernel"

    def displayName(self) -> str:
        return "Build Kernel Distance Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a kernel distance graph. Connects observations based on kernel "
            "density estimation with the specified bandwidth. "
            "Output is a table with source, target, and weight columns."
        )

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterNumber(
                self.BANDWIDTH,
                "Bandwidth",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1000.0,
                minValue=0.0,
            ),
            QgsProcessingParameterEnum(
                self.KERNEL,
                "Kernel type",
                options=["gaussian", "epanechnikov", "exponential", "triangular", "parabolic", "bisquare", "cosine", "boxcar", "identity"],
                defaultValue=0,  # gaussian
            ),
        ]

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        bandwidth = self.parameterAsDouble(parameters, self.BANDWIDTH, context)
        kernel_idx = self.parameterAsInt(parameters, self.KERNEL, context)
        kernel = ["gaussian", "epanechnikov", "exponential", "triangular", "parabolic", "bisquare", "cosine", "boxcar", "identity"][kernel_idx]
        # build_kernel requires Point geometries, so use centroids
        return Graph.build_kernel(gdf.centroid, bandwidth=bandwidth, kernel=kernel)


class BuildTriangulation(GraphAlgorithm):
    """Build triangulation graph."""

    def name(self) -> str:
        return "build_triangulation"

    def displayName(self) -> str:
        return "Build Triangulation Graph"

    def group(self) -> str:
        return "Graph"

    def groupId(self) -> str:
        return "graph"

    def shortHelpString(self) -> str:
        return (
            "Build a triangulation graph. Creates a Delaunay triangulation "
            "where each observation is connected to its natural neighbors. "
            "Output is a table with source, target, and weight columns."
        )

    def build_graph(self, gdf, parameters, context):
        from libpysal.graph import Graph
        # build_triangulation requires Point geometries, so use centroids
        return Graph.build_triangulation(gdf.centroid)


# Export all graph algorithms as strings for __all__
__all__ = [
    "BuildContiguity",
    "BuildDistanceBand",
    "BuildFuzzyContiguity",
    "BuildHigherOrder",
    "BuildKNN",
    "BuildKernel",
    "BuildTriangulation",
]
