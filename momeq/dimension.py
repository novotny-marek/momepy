import momepy

from .utils import qgs_to_gpd
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
)


class CourtyardArea(QgsProcessingAlgorithm):
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

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input layer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Output layer")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Convert QGIS source to GeoSeries and calculate courtyard area
        geometry_series = qgs_to_gpd(source)
        courtyard_area_series = momepy.courtyard_area(geometry_series)
        courtyard_area_values = courtyard_area_series.to_list()

        # Create output fields (original fields + new courtyard area field)
        fields = source.fields()
        fields.append(QgsField("courtyard_area", QVariant.Double))

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        # Get features from source
        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        # Process each feature directly
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new courtyard area
            attributes = feature.attributes()
            attributes.append(courtyard_area_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class LongestAxisLength(QgsProcessingAlgorithm):
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

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input layer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Output layer")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Convert QGIS source to GeoSeries and calculate longest axis length
        geometry_series = qgs_to_gpd(source)
        lal_series = momepy.longest_axis_length(geometry_series)
        lal_values = lal_series.to_list()

        # Create output fields (original fields + new longest axis length field)
        fields = source.fields()
        fields.append(QgsField("lal", QVariant.Double))

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        # Get features from source
        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        # Process each feature directly
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new longest axis length
            attributes = feature.attributes()
            attributes.append(lal_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class StreetProfile(QgsProcessingAlgorithm):
    INPUT = "INPUT_BUILDINGS"
    INPUT_STREETS = "INPUT_STREETS"
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
                "Input buildings layer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_STREETS,
                "Input street layer",
                [QgsProcessing.SourceType.VectorLine],
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
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
                defaultValue=None,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Output layer")
        )

    def processAlgorithm(self, parameters, context, feedback):
        polygon_source = self.parameterAsSource(parameters, self.INPUT, context)
        line_source = self.parameterAsSource(parameters, self.INPUT_STREETS, context)
        distance_field = self.parameterAsDouble(
            parameters, self.DISTANCE_FIELD, context
        )
        tick_length_field = self.parameterAsDouble(
            parameters, self.TICK_LENGTH_FIELD, context
        )
        height_field = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)

        # Convert QGIS source to GeoSeries and calculate street profile characters
        polygon_geometry_series = qgs_to_gpd(polygon_source)
        line_geometry_series = qgs_to_gpd(line_source)
        street_profile_series = momepy.street_profile(
            line_geometry_series,
            polygon_geometry_series,
            distance_field,
            tick_length_field,
            height_field,
        )
        street_profile_values = street_profile_series.to_list()

        # Create output fields (original fields + new street profile field)
        fields = polygon_source.fields()
        fields.append(QgsField("courtyard_area", QVariant.Double))

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            polygon_source.wkbType(),
            polygon_source.sourceCrs(),
        )

        # Get features from source
        features = polygon_source.getFeatures()
        total = (
            100.0 / polygon_source.featureCount()
            if polygon_source.featureCount()
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
            attributes.append(street_profile_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()
