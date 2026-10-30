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
        return momepy.longest_axis_length(geometry_series).to_list()


class PerimeterWall(QgsProcessingAlgorithm):
    pass


class StreetProfile(QgsProcessingAlgorithm):
    INPUT = "INPUT_STREETS"
    INPUT_BUILDINGS = "INPUT_BUILDINGS"
    OUTPUT = "OUTPUT"
    DISTANCE_FIELD = "DISTANCE_FIELD"
    TICK_LENGTH_FIELD = "TICK_LENGTH_FIELD"
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
        return "Calculates the street profile characters."

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input street network layer",
                [Qgis.ProcessingSourceType.VectorLine],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_BUILDINGS,
                "Input buildings layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_FIELD,
                "The distance between perpendicular ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TICK_LENGTH_FIELD,
                "The length of ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=50.0,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT_BUILDINGS,
                type=QgsProcessingParameterField.Numeric,
                defaultValue=None,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Street profile")
        )

    def processAlgorithm(self, parameters, context, feedback):
        line_source = self.parameterAsSource(parameters, self.INPUT, context)
        polygon_source = self.parameterAsSource(parameters, self.INPUT_BUILDINGS, context)
        distance_field = self.parameterAsDouble(
            parameters, self.DISTANCE_FIELD, context
        )
        tick_length_field = self.parameterAsDouble(
            parameters, self.TICK_LENGTH_FIELD, context
        )
        height_field = self.parameterAsString(parameters, self.HEIGHT_FIELD, context) or None

        # Convert QGIS source to GeoSeries and calculate street profile characters
        polygon_geometry_dataframe = qgs_to_gpd(polygon_source, attribute_fields=height_field)
        line_geometry_series = qgs_to_gpd(line_source)
        if height_field:
            height = polygon_geometry_dataframe[height_field]
        else:
            height = None
        street_profile_series = momepy.street_profile(
            line_geometry_series,
            polygon_geometry_dataframe,
            distance_field,
            tick_length_field,
            height,
        )
        street_profile_values = street_profile_series.to_dict()
        width_values = street_profile_values["width"]
        openness_values = street_profile_values["openness"]
        width_deviation_values = street_profile_values["width_deviation"]
        if height_field:
            height_values = street_profile_values["height"]
            height_deviation_values = street_profile_values["height_deviation"]
            hw_ratio_values = street_profile_values["hw_ratio"]

        # Create output fields (original fields + new street profile fields)
        fields = line_source.fields()
        fields.append(QgsField("width", QMetaType.Type.Double))
        fields.append(QgsField("openness", QMetaType.Type.Double))
        fields.append(QgsField("width_deviation", QMetaType.Type.Double))

        if height_field:
            fields.append(QgsField("height", QMetaType.Type.Double))
            fields.append(QgsField("height_deviation", QMetaType.Type.Double))
            fields.append(QgsField("hw_ratio", QMetaType.Type.Double))

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            line_source.wkbType(),
            line_source.sourceCrs(),
        )

        # Get features from source
        features = line_source.getFeatures()
        total = (
            100.0 / line_source.featureCount()
            if line_source.featureCount()
            else 0
        )

        # Process each feature directly
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new street profile
            attributes = feature.attributes()
            
            attributes.append(width_values[current])
            attributes.append(openness_values[current])
            attributes.append(width_deviation_values[current])
            if height_field:
                attributes.append(height_values[current])
                attributes.append(height_deviation_values[current])
                attributes.append(hw_ratio_values[current])

            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class WeightedCharacter(QgsProcessingAlgorithm):
    pass
