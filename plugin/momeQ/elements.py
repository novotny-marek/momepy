import json

import momepy

from .utils import qgs_to_gpd
from .base import MomeQGeometryAlgorithm, MomeQProcessingAlgorithm, shapely_to_qgs_geometry
from PyQt6.QtCore import QMetaType
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsFields,
    QgsWkbTypes,
)


class BufferedLimit(MomeQGeometryAlgorithm):
    ADAPTIVE = "ADAPTIVE"
    BUFFER = "BUFFER"
    MIN_BUFFER = "MIN_BUFFER"
    MAX_BUFFER = "MAX_BUFFER"

    def name(self) -> str:
        return "buffered_limit"

    def displayName(self) -> str:
        return "Buffered limit"

    def group(self) -> str:
        return "Elements"

    def groupId(self) -> str:
        return "elements"

    def shortHelpString(self) -> str:
        return "Define a limit for tesselation as a buffer around buildings."

    def input_layer_name(self): return "Buildings"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterBoolean(self.ADAPTIVE, "Adaptive (Gabriel graph)", defaultValue=False),
            QgsProcessingParameterNumber(self.BUFFER, "Buffer distance", QgsProcessingParameterNumber.Double, defaultValue=100),
            QgsProcessingParameterNumber(self.MIN_BUFFER, "Min adaptive buffer", QgsProcessingParameterNumber.Double, defaultValue=0),
            QgsProcessingParameterNumber(self.MAX_BUFFER, "Max adaptive buffer", QgsProcessingParameterNumber.Double, defaultValue=100),
        ]

    def output_wkb_type(self, source):
        return Qgis.WkbType.Unknown

    def run_momepy(self, gdf, parameters, context):
        buffer = "adaptive" if self.parameterAsBool(parameters, self.ADAPTIVE, context) else \
            self.parameterAsDouble(parameters, self.BUFFER, context)
        limit = momepy.buffered_limit(
            gdf, buffer=buffer,
            min_buffer=self.parameterAsDouble(parameters, self.MIN_BUFFER, context),
            max_buffer=self.parameterAsDouble(parameters, self.MAX_BUFFER, context),
        )
        return [limit]


class MorphologicalTessellation(MomeQGeometryAlgorithm):
    CLIP = "CLIP"
    SHRINK = "SHRINK"
    SEGMENT = "SEGMENT"
    CLIP_OPTIONS = ["bounding_box", "convex_hull", "alpha_shape", "none"]
    CLIP_LIMIT = "CLIP_LIMIT"

    def name(self) -> str:
        return "morphological_tessellation"

    def displayName(self) -> str:
        return "Morphological tessellation"

    def group(self) -> str:
        return "Elements"

    def groupId(self) -> str:
        return "elements"

    def shortHelpString(self) -> str:
        return "Generates morphological tessellation."

    def input_layer_name(self): return "Buildings"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterEnum(self.CLIP, "Clip", self.CLIP_OPTIONS, defaultValue=0),
            QgsProcessingParameterFeatureSource(
                self.CLIP_LIMIT,
                "Buffered limit layer (optional, overrides Clip)",
                [Qgis.ProcessingSourceType.VectorPolygon],
                optional=True,
            ),
            QgsProcessingParameterNumber(self.SHRINK, "Shrink distance", QgsProcessingParameterNumber.Double, defaultValue=0.4),
            QgsProcessingParameterNumber(self.SEGMENT, "Max segment length", QgsProcessingParameterNumber.Double, defaultValue=0.5),
        ]

    def output_wkb_type(self, source):
        return Qgis.WkbType.Unknown

    def output_fields(self, parameters=None, context=None):
        return [QgsField("building_idx", QMetaType.Type.LongLong)]

    def run_momepy(self, gdf, parameters, context):
        limit_source = self.parameterAsSource(parameters, self.CLIP_LIMIT, context)
        if limit_source:
            # A buffered limit (e.g. from the "Buffered limit" algorithm)
            # overrides the clip method enum.
            clip = qgs_to_gpd(limit_source)
        else:
            clip = self.CLIP_OPTIONS[self.parameterAsEnum(parameters, self.CLIP, context)]
            if clip == "none":
                clip = None
        self._result = momepy.morphological_tessellation(
            gdf,
            clip=clip,
            shrink=self.parameterAsDouble(parameters, self.SHRINK, context),
            segment=self.parameterAsDouble(parameters, self.SEGMENT, context),
        )
        return self._result

    def row_attributes(self, index, row):
        return [index]

class EnclosedTessellation(MomeQGeometryAlgorithm):
    ENCLOSURES = "ENCLOSURES"
    SHRINK = "SHRINK"
    SEGMENT = "SEGMENT"
    THRESHOLD = "THRESHOLD"
    N_JOBS = "N_JOBS"
    INNER_BARRIERS = "INNER_BARRIERS"
    CELL_SIZE = "CELL_SIZE"
    NEIGHBOR_MODE = "NEIGHBOR_MODE"

    def name(self):
        return "enclosed_tessellation"

    def displayName(self):
        return "Enclosed tessellation"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self): 
        return "Morphological tessellation within enclosures; with inner barriers it uses the CA implementation."

    def input_layer_name(self):
        return "Buildings"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterFeatureSource(
                self.ENCLOSURES,
                "Enclosures",
                [Qgis.ProcessingSourceType.VectorPolygon],
            ),
            QgsProcessingParameterNumber(
                self.SHRINK,
                "Shrink distance",
                QgsProcessingParameterNumber.Double,
                defaultValue=0.4,
            ),
            QgsProcessingParameterNumber(
                self.SEGMENT,
                "Max segment length",
                QgsProcessingParameterNumber.Double,
                defaultValue=0.5,
            ),
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                "Building-in-enclosure area ratio (-1 = skip check)",
                QgsProcessingParameterNumber.Double,
                defaultValue=0.05,
            ),
            QgsProcessingParameterNumber(
                self.N_JOBS,
                "Parallel jobs",
                QgsProcessingParameterNumber.Integer,
                defaultValue=-1,
            ),
            QgsProcessingParameterFeatureSource(
                self.INNER_BARRIERS,
                "Inner barriers (optional, enables CA)",
                [Qgis.ProcessingSourceType.VectorLine],
                optional=True,
            ),
            QgsProcessingParameterNumber(
                self.CELL_SIZE,
                "CA cell size",
                QgsProcessingParameterNumber.Double,
                defaultValue=1,
            ),
            QgsProcessingParameterEnum(
                self.NEIGHBOR_MODE,
                "CA neighbor mode",
                ["moore", "neumann"],
                defaultValue=0,
            ),
        ]

    def output_wkb_type(self, source):
        return Qgis.WkbType.Unknown

    def output_fields(self, parameters=None, context=None):
        return [
            QgsField("building_idx", QMetaType.Type.LongLong),
            QgsField("enclosure_idx", QMetaType.Type.LongLong),
        ]

    def run_momepy(self, gdf, parameters, context):
        inner = self.parameterAsSource(parameters, self.INNER_BARRIERS, context)
        threshold = self.parameterAsDouble(parameters, self.THRESHOLD, context)
        self._result = momepy.enclosed_tessellation(
            gdf,
            qgs_to_gpd(self.parameterAsSource(parameters, self.ENCLOSURES, context)),
            shrink=self.parameterAsDouble(parameters, self.SHRINK, context),
            segment=self.parameterAsDouble(parameters, self.SEGMENT, context),
            threshold=threshold if threshold >= 0 else None,
            n_jobs=self.parameterAsInt(parameters, self.N_JOBS, context),
            inner_barriers=qgs_to_gpd(inner) if inner else None,
            cell_size=self.parameterAsDouble(parameters, self.CELL_SIZE, context),
            neighbor_mode=["moore", "neumann"][self.parameterAsEnum(parameters, self.NEIGHBOR_MODE, context)],
        )

        return self._result

    def row_attributes(self, index, row):
        enc_col = next(c for c in self._result.columns if c != self._result.geometry.name)

        return [index, row[enc_col]]

class Enclosures(MomeQGeometryAlgorithm):
    LIMIT = "LIMIT"
    ENCLOSURE_ID = "ENCLOSURE_ID"
    CLIP = "CLIP"

    def name(self):
        return "enclosures"

    def displayName(self):
        return "Enclosures"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Enclosed areas from primary barriers (roads, railways, rivers) and an optional limit."

    def input_layer_name(self):
        return "Primary barriers (lines)"

    def input_geometry_types(self):
        return [Qgis.ProcessingSourceType.VectorLine]

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterFeatureSource(self.LIMIT, "External limit (optional)", [Qgis.ProcessingSourceType.VectorPolygon], optional=True),
            QgsProcessingParameterString(self.ENCLOSURE_ID, "Enclosure ID field name", defaultValue="eID"),
            QgsProcessingParameterBoolean(self.CLIP, "Clip enclosures to the limit", defaultValue=False),
        ]

    def output_wkb_type(self, source):
        return Qgis.WkbType.Unknown

    def output_fields(self, parameters=None, context=None):
        eid = self.parameterAsString(parameters, self.ENCLOSURE_ID, context) if parameters else "eID"
        
        return [QgsField(eid, QMetaType.Type.LongLong)]

    def run_momepy(self, gdf, parameters, context):
        limit_source = self.parameterAsSource(parameters, self.LIMIT, context)
        self._eid = self.parameterAsString(parameters, self.ENCLOSURE_ID, context)
        self._result = momepy.enclosures(
            gdf,
            limit=qgs_to_gpd(limit_source) if limit_source else None,
            enclosure_id=self._eid,
            clip=self.parameterAsBool(parameters, self.CLIP, context),
        )
        return self._result

    def row_attributes(self, index, row):
        return [row[self._eid]]

class ProximityBands(MomeQGeometryAlgorithm):
    BAND = "BAND"
    SHRINK = "SHRINK"
    SEGMENT = "SEGMENT"
    SINGLE_SIDED = "SINGLE_SIDED"

    def name(self):
        return "proximity_bands"

    def displayName(self):
        return "Proximity bands"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Bands within a fixed distance around street segments (single-sided requires neatnet)."

    def input_layer_name(self):
        return "Street segments (lines)"

    def input_geometry_types(self):
        return [Qgis.ProcessingSourceType.VectorLine]

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterNumber(self.BAND, "Band distance", QgsProcessingParameterNumber.Double, defaultValue=20),
            QgsProcessingParameterNumber(self.SHRINK, "End shrink (fraction of length)", QgsProcessingParameterNumber.Double, defaultValue=0.001),
            QgsProcessingParameterNumber(self.SEGMENT, "Max segment length", QgsProcessingParameterNumber.Double, defaultValue=2),
            QgsProcessingParameterBoolean(self.SINGLE_SIDED, "Split bands per side (requires neatnet)", defaultValue=False),
        ]

    def output_wkb_type(self, source):
        return Qgis.WkbType.Unknown

    def run_momepy(self, gdf, parameters, context):
        return momepy.proximity_bands(
            gdf,
            band=self.parameterAsDouble(parameters, self.BAND, context),
            shrink=self.parameterAsDouble(parameters, self.SHRINK, context),
            segment=self.parameterAsDouble(parameters, self.SEGMENT, context),
            single_sided=self.parameterAsBool(parameters, self.SINGLE_SIDED, context),
        )

class GenerateBlocks(QgsProcessingAlgorithm):
    """Two-output algorithm — deliberately outside both bases: QGIS
    multi-sink needs a second parameterAsSink call, which the single-sink
    bases do not model."""
    INPUT_TESSELLATION = "INPUT_TESSELLATION"
    INPUT_EDGES = "INPUT_EDGES"
    INPUT_BUILDINGS = "INPUT_BUILDINGS"
    OUTPUT_BLOCKS = "OUTPUT_BLOCKS"
    OUTPUT_IDS = "OUTPUT_IDS"

    def name(self):
        return "generate_blocks"

    def displayName(self):
        return "Generate blocks"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Dissolve tessellation into blocks using the street network; also links block IDs to cells."

    def initAlgorithm(self, configuration=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_TESSELLATION, "Morphological tessellation", [Qgis.ProcessingSourceType.VectorPolygon]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_EDGES, "Street network edges", [Qgis.ProcessingSourceType.VectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_BUILDINGS, "Buildings", [Qgis.ProcessingSourceType.VectorPolygon]))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_BLOCKS, "Blocks"))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_IDS, "Block ID per tessellation cell"))

    def processAlgorithm(self, parameters, context, feedback):
        tess_source = self.parameterAsSource(parameters, self.INPUT_TESSELLATION, context)
        tess = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_TESSELLATION, context))
        edges = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_EDGES, context))
        buildings = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_BUILDINGS, context))

        # momepy.generate_blocks -> (blocks GeoDataFrame, tessellation-id Series)
        blocks, tess_ids = momepy.generate_blocks(tess, edges, buildings)

        block_fields = QgsFields()
        block_fields.append(QgsField("block_id", QMetaType.Type.LongLong))
        # Convert geometries up-front and derive the WKB type from the data:
        # memory sinks (TEMPORARY_OUTPUT) cannot be created with
        # Qgis.WkbType.Unknown.
        block_geometries = [shapely_to_qgs_geometry(g) for g in blocks.geometry]
        block_wkb_type = (
            block_geometries[0].wkbType()
            if block_geometries
            else Qgis.WkbType.NoGeometry
        )
        (sink, dest) = self.parameterAsSink(
            parameters, self.OUTPUT_BLOCKS, context, block_fields,
            block_wkb_type, tess.crs(),
        )
        total = 100.0 / len(block_geometries) if block_geometries else 0
        for i, geom in enumerate(block_geometries):
            if feedback.isCanceled():
                break
            f = QgsFeature(block_fields)
            f.setGeometry(geom)
            sink.addFeature(f, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(int(i * total))

        # Geometrically-free join table: tessellation index -> block id.
        id_fields = QgsFields()
        id_fields.append(QgsField("tessellation_idx", QMetaType.Type.LongLong))
        id_fields.append(QgsField("block_id", QMetaType.Type.LongLong))
        (sink2, dest2) = self.parameterAsSink(
            parameters, self.OUTPUT_IDS, context, id_fields,
            Qgis.WkbType.NoGeometry, tess_source.sourceCrs(),
        )
        for idx, bid in tess_ids.items():
            f = QgsFeature(id_fields)
            f.setAttributes([idx, bid])
            sink2.addFeature(f, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT_BLOCKS: dest, self.OUTPUT_IDS: dest2}

    def createInstance(self):
        return self.__class__()

class GetNearestStreet(MomeQProcessingAlgorithm):
    INPUT_STREETS = "INPUT_STREETS"
    MAX_DISTANCE = "MAX_DISTANCE"

    def name(self):
        return "get_nearest_street"

    def displayName(self):
        return "Get nearest street"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Index of the nearest street for each building (feed into Street alignment / Get nearest node)."

    def input_layer_name(self):
        return "Buildings"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterFeatureSource(self.INPUT_STREETS, "Streets", [Qgis.ProcessingSourceType.VectorLine]),
            # QGIS numbers cannot be null; -1 means "no limit".
            QgsProcessingParameterNumber(self.MAX_DISTANCE, "Max distance (-1 = unlimited)", QgsProcessingParameterNumber.Double, defaultValue=-1),
        ]

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("nearest_street", QMetaType.Type.LongLong)]

    def calculate_values(self, source, parameters, context):
        streets = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_STREETS, context))
        d = self.parameterAsDouble(parameters, self.MAX_DISTANCE, context)
        return momepy.get_nearest_street(
            qgs_to_gpd(source), streets, max_distance=d if d >= 0 else None
        ).to_list()

class GetNearestNode(MomeQProcessingAlgorithm):
    INPUT_NODES = "INPUT_NODES"
    INPUT_EDGES = "INPUT_EDGES"
    NEAREST_EDGE = "NEAREST_EDGE"

    def name(self):
        return "get_nearest_node"

    def displayName(self):
        return "Get nearest node"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Closest endpoint node on each building's nearest edge. Edges need node_start/node_end columns (momepy.nx_to_gdf structure)."

    def input_layer_name(self):
        return "Buildings"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterFeatureSource(self.INPUT_NODES, "Network nodes", [Qgis.ProcessingSourceType.VectorPoint]),
            QgsProcessingParameterFeatureSource(self.INPUT_EDGES, "Network edges (with node_start/node_end)", [Qgis.ProcessingSourceType.VectorLine]),
            QgsProcessingParameterField(self.NEAREST_EDGE, "Nearest edge field (from Get nearest street)", parentLayerParameterName=self.INPUT, type=QgsProcessingParameterField.Numeric),
        ]

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("nearest_node", QMetaType.Type.LongLong)]

    def calculate_values(self, source, parameters, context):
        nodes = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_NODES, context))
        edges = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_EDGES, context))
        f = self.parameterAsString(parameters, self.NEAREST_EDGE, context)
        gdf = qgs_to_gpd(source, attribute_fields=[f])
        return momepy.get_nearest_node(gdf, nodes, edges, gdf[f]).to_list()

class GetNetworkRatio(MomeQProcessingAlgorithm):
    INPUT_EDGES = "INPUT_EDGES"
    INITIAL_BUFFER = "INITIAL_BUFFER"

    def name(self):
        return "get_network_ratio"

    def displayName(self):
        return "Get network ratio"

    def group(self):
        return "Elements"

    def groupId(self):
        return "elements"

    def shortHelpString(self):
        return "Proportion of overlap between cells and network edges, as JSON key/value strings (edge IDs are integer positions)."

    def input_layer_name(self):
        return "Cells (e.g. enclosed tessellation)"

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterFeatureSource(self.INPUT_EDGES, "Street network edges", [Qgis.ProcessingSourceType.VectorLine]),
            QgsProcessingParameterNumber(self.INITIAL_BUFFER, "Initial buffer for non-intersecting cells", QgsProcessingParameterNumber.Double, defaultValue=500),
        ]

    def get_output_fields(self, parameters=None, context=None):
        return [
            QgsField("edgeID_keys", QMetaType.Type.String),
            QgsField("edgeID_values", QMetaType.Type.String),
        ]

    def calculate_values(self, source, parameters, context):
        edges = qgs_to_gpd(self.parameterAsSource(parameters, self.INPUT_EDGES, context))
        result = momepy.get_network_ratio(
            qgs_to_gpd(source),
            edges,
            initial_buffer=self.parameterAsDouble(parameters, self.INITIAL_BUFFER, context),
        )
        return [
            (json.dumps(r.edgeID_keys), json.dumps(r.edgeID_values))
            for r in result.itertuples(index=False)
        ]
