import momepy

from typing import List
from .utils import qgs_to_gpd
from .base import MomeQProcessingAlgorithm
from PyQt6.QtCore import QMetaType
from qgis.core import (
    Qgis,
    QgsField,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
)


class Orientation(MomeQProcessingAlgorithm):
    def name(self) -> str:
        return "orientation"

    def displayName(self) -> str:
        return "Orientation"

    def group(self) -> str:
        return "Distribution"

    def groupId(self) -> str:
        return "distribution"

    def shortHelpString(self) -> str:
        return (
            "Calculates the orientation of objects. The orientation is defined as the "
            "deviation of orientation of the bounding rectangle from cardinal directions. "
            "As such it is within a range 0 - 45 degrees. For LineStrings, it represents "
            "the orientation of the line connecting the first and the last point of the segment."
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [
            Qgis.ProcessingSourceType.VectorPolygon,
            Qgis.ProcessingSourceType.VectorLine,
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("orientation", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        geometry_series = qgs_to_gpd(source)
        return momepy.orientation(geometry_series).to_list()


class SharedWalls(MomeQProcessingAlgorithm):
    STRICT = "STRICT"
    TOLERANCE = "TOLERANCE"

    def name(self) -> str:
        return "shared_walls"

    def displayName(self) -> str:
        return "Shared walls"

    def group(self) -> str:
        return "Distribution"

    def groupId(self) -> str:
        return "distribution"

    def shortHelpString(self) -> str:
        return (
            "Calculates the length of shared walls of adjacent elements (typically buildings). "
            "Note that data needs to be topologically correct. Overlapping polygons will lead to "
            "incorrect results."
        )

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterBoolean(
                self.STRICT,
                "Strict contiguity",
                defaultValue=True,
            ),
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                "Tolerance",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.01,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("shared_walls", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        geometry_series = qgs_to_gpd(source)
        strict = self.parameterAsBool(parameters, self.STRICT, context)
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        return momepy.shared_walls(geometry_series, strict=strict, tolerance=tolerance).to_list()


class CellAlignment(MomeQProcessingAlgorithm):
    INPUT_CELLS = "INPUT_CELLS"
    INPUT_BUILDINGS = "INPUT_BUILDINGS"

    def name(self) -> str:
        return "cell_alignment"

    def displayName(self) -> str:
        return "Cell alignment"

    def group(self) -> str:
        return "Distribution"

    def groupId(self) -> str:
        return "distribution"

    def shortHelpString(self) -> str:
        return (
            "Calculates the difference between cell orientation and building orientation. "
            "Requires two input layers: morphological tessellation cells and buildings."
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def input_layer_name(self) -> str:
        return "Input buildings layer"

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterFeatureSource(
                self.INPUT_CELLS,
                "Input tessellation cells layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("cell_alignment", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        # Get buildings layer (from main INPUT)
        buildings_source = source
        
        # Get tessellation cells layer (from additional parameter)
        cells_source = self.parameterAsSource(parameters, self.INPUT_CELLS, context)
        
        # Convert both to GeoDataFrames
        buildings_gdf = qgs_to_gpd(buildings_source)
        cells_gdf = qgs_to_gpd(cells_source)
        
        # Calculate orientations for both
        building_orientations = momepy.orientation(buildings_gdf)
        cell_orientations = momepy.orientation(cells_gdf)
        
        # Calculate cell alignment
        return momepy.cell_alignment(cell_orientations, building_orientations).to_list()


class StreetAlignment(MomeQProcessingAlgorithm):
    INPUT_STREETS = "INPUT_STREETS"
    STREET_INDEX_FIELD = "STREET_INDEX_FIELD"

    def name(self) -> str:
        return "street_alignment"

    def displayName(self) -> str:
        return "Street alignment"

    def group(self) -> str:
        return "Distribution"

    def groupId(self) -> str:
        return "distribution"

    def shortHelpString(self) -> str:
        return (
            "Calculates the deviation of the building orientation from the street orientation. "
            "Requires buildings layer (polygons) and streets layer (linestrings), "
            "plus a street index field mapping buildings to streets."
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def input_layer_name(self) -> str:
        return "Input buildings layer"

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterFeatureSource(
                self.INPUT_STREETS,
                "Input streets layer",
                [Qgis.ProcessingSourceType.VectorLine],
            ),
            QgsProcessingParameterField(
                self.STREET_INDEX_FIELD,
                "Street index field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("street_alignment", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        # Get buildings layer (from main INPUT)
        buildings_source = source
        
        # Get streets layer (from additional parameter)
        streets_source = self.parameterAsSource(parameters, self.INPUT_STREETS, context)
        
        # Get street index field
        street_index_field = self.parameterAsString(parameters, self.STREET_INDEX_FIELD, context)
        
        # Convert to GeoDataFrames
        buildings_gdf = qgs_to_gpd(buildings_source, attribute_fields=[street_index_field])
        streets_gdf = qgs_to_gpd(streets_source)
        
        # Calculate orientations
        building_orientations = momepy.orientation(buildings_gdf)
        street_orientations = momepy.orientation(streets_gdf)
        
        # Get street index series
        street_index = buildings_gdf[street_index_field]
        
        # Calculate street alignment
        return momepy.street_alignment(building_orientations, street_orientations, street_index).to_list()