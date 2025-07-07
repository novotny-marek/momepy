import momepy

from typing import List, Union
from .utils import qgs_to_gpd
from .base import MomepyProcessingAlgorithm
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
    QgsProcessingParameterBoolean,
)


class FormFactor(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    HEIGHT_FIELD = "HEIGHT_FIELD"

    def name(self) -> str:
        return "form_factor"

    def displayName(self) -> str:
        return "Form factor"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return (
            "Calculates the form factor of each object given its geometry and height."
        )

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            )
        )

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Form factor"))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        height_field = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)

        # Convert QGIS feature to GeoDataFrame and calculate form factor
        geometry_dataframe = qgs_to_gpd(source, attribute_fields=[height_field])
        height = geometry_dataframe[height_field]
        form_factor_series = momepy.form_factor(geometry_dataframe, height)
        form_factor_values = form_factor_series.to_list()

        # Create output fields (original fields + new form factor field)
        fields = source.fields()
        fields.append(QgsField("form_factor", QMetaType.Type.Double))

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

            # Copy attributes and add new form factor
            attributes = feature.attributes()
            attributes.append(form_factor_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class FractalDimension(MomepyProcessingAlgorithm):
    def name(self) -> str:
        return "fractal_dimension"

    def displayName(self) -> str:
        return "Fractal dimension"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates fractal dimension based on area and perimeter."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("fractal_dimension", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.fractal_dimension(geometry_series).to_list()


class FacadeRatio(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "facade_ratio"

    def displayName(self) -> str:
        return "Facade ratio"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the facade ratio of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("facade_ratio", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.facade_ratio(geometry_series).to_list()


class CircularCompactness(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "circular_compactness"

    def displayName(self) -> str:
        return "Circular compactness"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the circular compactness of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("circular_compactness", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.circular_compactness(geometry_series).to_list()


class SquareCompactness(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "square_compactness"

    def displayName(self) -> str:
        return "Square compactness"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the square compactness of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("square_compactness", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.square_compactness(geometry_series).to_list()


class Convexity(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "convexity"

    def displayName(self) -> str:
        return "Convexity"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the convexity of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("convexity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.convexity(geometry_series).to_list()


class CourtyardIndex(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    COURTYARD_AREA_FIELD = "COURTYARD_AREA_FIELD"

    def name(self) -> str:
        return "courtyard_index"

    def displayName(self) -> str:
        return "Courtyard index"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the courtyard index of each object given its geometry."

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.COURTYARD_AREA_FIELD,
                "Courtyard area field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Courtyard index")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        courtyard_area_field = self.parameterAsString(
            parameters, self.COURTYARD_AREA_FIELD, context
        )

        # Convert QGIS feature to GeoDataFrame and calculate courtyard index
        geometry_dataframe = qgs_to_gpd(source, attribute_fields=[courtyard_area_field])
        courtyard_area = geometry_dataframe[courtyard_area_field]
        courtyard_index_series = momepy.courtyard_index(
            geometry_dataframe, courtyard_area=courtyard_area
        )
        courtyard_index_values = courtyard_index_series.to_list()

        # Create output fields (original fields + new courtyard index field)
        fields = source.fields()
        fields.append(QgsField("courtyard_index", QMetaType.Type.Double))

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

            # Copy attributes and add new courtyard index
            attributes = feature.attributes()
            attributes.append(courtyard_index_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class Rectangularity(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "rectangularity"

    def displayName(self) -> str:
        return "Rectangularity"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the rectangularity of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("rectangularity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.rectangularity(geometry_series).to_list()


class ShapeIndex(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    LONGEST_AXIS_FIELD = "LONGEST_AXIS_FIELD"

    def name(self) -> str:
        return "shape_index"

    def displayName(self) -> str:
        return "Shape index"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the shape index of each object given its geometry."

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.LONGEST_AXIS_FIELD,
                "Longest axis length field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            )
        )

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Shape index"))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        longest_axis_field = self.parameterAsString(
            parameters, self.LONGEST_AXIS_FIELD, context
        )

        # Convert QGIS feature to GeoDataFrame and calculate shape index
        geometry_dataframe = qgs_to_gpd(source, attribute_fields=[longest_axis_field])
        longest_axis = geometry_dataframe[longest_axis_field]
        shape_index_series = momepy.shape_index(
            geometry_dataframe, longest_axis_length=longest_axis
        )
        shape_index_values = shape_index_series.to_list()

        # Create output fields (original fields + new shape index field)
        fields = source.fields()
        fields.append(QgsField("shape_index", QMetaType.Type.Double))

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

            # Copy attributes and add new shape index
            attributes = feature.attributes()
            attributes.append(shape_index_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class Corners(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    EPS_FIELD = "EPS_FIELD"
    INTERIORS_FIELD = "INTERIORS_FIELD"

    def name(self) -> str:
        return "corners"

    def displayName(self) -> str:
        return "Corners"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the number of corners of each object given its geometry."

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                "Deviation from 180 degrees to consider a corner, by default 10.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                "Include polygon interiors, by default False.",
                defaultValue=False,
                optional=True,
            )
        )

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Corners"))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(
            parameters, self.INTERIORS_FIELD, context
        )

        # Convert QGIS feature to GeoSeries and calculate number of corners
        geometry_series = qgs_to_gpd(source)
        corners_series = momepy.corners(
            geometry_series, eps=eps_field, include_interiors=interiors_field
        )
        corners_values = corners_series.to_list()

        fields = source.fields()
        fields.append(QgsField("corners", QMetaType.Type.Int))

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

            # Copy attributes and add new corners
            attributes = feature.attributes()
            attributes.append(corners_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class Squareness(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    EPS_FIELD = "EPS_FIELD"
    INTERIORS_FIELD = "INTERIORS_FIELD"

    def name(self) -> str:
        return "squareness"

    def displayName(self) -> str:
        return "Squareness"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the squareness of each object given its geometry."

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                "Deviation from 180 degrees to consider a corner, by default 10.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                "Include polygon interiors, by default False.",
                defaultValue=False,
                optional=True,
            )
        )

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Squareness"))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(
            parameters, self.INTERIORS_FIELD, context
        )

        # Convert QGIS feature to GeoSeries and calculate squareness
        geometry_series = qgs_to_gpd(source)
        squareness_series = momepy.squareness(
            geometry_series, eps=eps_field, include_interiors=interiors_field
        )
        squareness_values = squareness_series.to_list()

        fields = source.fields()
        fields.append(QgsField("squareness", QMetaType.Type.Double))

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

            # Copy attributes and add new squareness
            attributes = feature.attributes()
            attributes.append(squareness_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class EquivalentRectangularIndex(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "equivalent_rectangular_index"

    def displayName(self) -> str:
        return "Equivalent rectangular index"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the equivalent rectangular index of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("equivalent_rectangular_index", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.equivalent_rectangular_index(geometry_series).to_list()


class Elongation(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "elongation"

    def displayName(self) -> str:
        return "Elongation"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the elongation of each object given its geometry."

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("elongation", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.elongation(geometry_series).to_list()


class CentroidCornerDistance(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    EPS_FIELD = "EPS_FIELD"
    INTERIORS_FIELD = "INTERIORS_FIELD"

    def name(self) -> str:
        return "centroid_corner_distance"

    def displayName(self) -> str:
        return "Centroid corner distance"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return (
            "Calculates the centroid corner distance of each object given its geometry."
        )

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                "Deviation from 180 degrees to consider a corner, by default 10.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                "Include polygon interiors, by default False.",
                defaultValue=False,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Centroid corner distance")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(
            parameters, self.INTERIORS_FIELD, context
        )

        # Convert QGIS feature to GeoSeries and calculate centroid corner distance
        geometry_series = qgs_to_gpd(source)
        ccd_series = momepy.centroid_corner_distance(
            geometry_series, eps=eps_field, include_interiors=interiors_field
        )
        ccd_values = ccd_series.to_list()

        fields = source.fields()
        fields.append(QgsField("centroid_corner_distance", QMetaType.Type.Double))

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

            # Copy attributes and add new centroid corner distance
            attributes = feature.attributes()
            attributes.append(ccd_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()


class Linearity(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "linearity"

    def displayName(self) -> str:
        return "Linearity"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return "Calculates the linearity of each LineString."

    def initAlgorithm(self, configuratio=None):
        """Initialize algorithm with input/output plus additional parameters."""
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorLine],
            )
        )

        # Add algorithm-specific parameters
        for param in self.get_additional_parameters():
            self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.displayName())
        )

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("linearity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.linearity(geometry_series).to_list()


class CompactnessWeightedAxis(MomepyProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "compactness_weighted_axis"

    def displayName(self) -> str:
        return "Compactness weighted axis"

    def group(self) -> str:
        return "Shape"

    def groupId(self) -> str:
        return "shape"

    def shortHelpString(self) -> str:
        return (
            "Calculates the compactness-weighted axis of each object in a given layer."
        )

    def get_output_fields(self) -> List[QgsField]:
        return [QgsField("compactness_weighted_axis", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        geometry_series = qgs_to_gpd(source)
        return momepy.compactness_weighted_axis(geometry_series).to_list()


class SunlightOptimised(QgsProcessingAlgorithm):
    pass
