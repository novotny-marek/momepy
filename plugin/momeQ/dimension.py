import momepy

from typing import List, Union
from .base import MomeQProcessingAlgorithm
from .utils import qgs_to_gpd
from PyQt6.QtCore import QMetaType
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
)


class Volume(QgsProcessingAlgorithm):
    pass


class FloorArea(QgsProcessingAlgorithm):
    pass


class CourtyardArea(MomeQProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "courtyard_area"

    def displayName(self) -> str:
        return "Courtyard area"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates area of holes within geometry - area of courtyards."

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("courtyard_area", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.courtyard_area(geometry_series).to_list()


class LongestAxisLength(MomeQProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "longest_axis_length"

    def displayName(self) -> str:
        return "Longest axis length"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates the length of the longest axis of object."

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("longest_axis_length", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.longest_axis_length(geometry_series).to_list()


class PerimeterWall(QgsProcessingAlgorithm):
    pass


class StreetProfile(MomeQProcessingAlgorithm):
    INPUT_BUILDINGS = "INPUT_BUILDINGS"
    DISTANCE = "DISTANCE"
    TICK_LENGTH = "TICK_LENGTH"
    HEIGHT_FIELD = "HEIGHT_FIELD"

    def name(self) -> str:
        return "street_profile"

    def displayName(self) -> str:
        return "Street profile"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return (
            "Calculates the street profile characters: width, openness and "
            "width deviation; with a building height field also height, "
            "height deviation and the height/width ratio."
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [Qgis.ProcessingSourceType.VectorLine]

    def input_layer_name(self) -> str:
        return "Input street network layer"

    def get_additional_parameters(self) -> List:
        return [
            QgsProcessingParameterFeatureSource(
                self.INPUT_BUILDINGS,
                "Input buildings layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            ),
            QgsProcessingParameterNumber(
                self.DISTANCE,
                "The distance between perpendicular ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
            ),
            QgsProcessingParameterNumber(
                self.TICK_LENGTH,
                "The length of ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=50.0,
            ),
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT_BUILDINGS,
                type=QgsProcessingParameterField.Numeric,
                defaultValue=None,
                optional=True,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        fields = [
            QgsField("width", QMetaType.Type.Double),
            QgsField("openness", QMetaType.Type.Double),
            QgsField("width_deviation", QMetaType.Type.Double),
        ]
        if parameters is not None and self.parameterAsString(
            parameters, self.HEIGHT_FIELD, context
        ):
            fields.extend(
                [
                    QgsField("height", QMetaType.Type.Double),
                    QgsField("height_deviation", QMetaType.Type.Double),
                    QgsField("hw_ratio", QMetaType.Type.Double),
                ]
            )
        return fields

    def calculate_values(self, source, parameters, context):
        building_source = self.parameterAsSource(
            parameters, self.INPUT_BUILDINGS, context
        )
        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)
        tick_length = self.parameterAsDouble(parameters, self.TICK_LENGTH, context)
        height_field = (
            self.parameterAsString(parameters, self.HEIGHT_FIELD, context) or None
        )

        buildings = qgs_to_gpd(building_source, attribute_fields=height_field)
        streets = qgs_to_gpd(source)
        heights = buildings[height_field] if height_field else None

        result = momepy.street_profile(
            streets, buildings, distance, tick_length, heights
        )

        columns = ["width", "openness", "width_deviation"]
        if height_field:
            columns += ["height", "height_deviation", "hw_ratio"]

        return list(zip(*[result[c].to_list() for c in columns]))


class WeightedCharacter(QgsProcessingAlgorithm):
    pass
