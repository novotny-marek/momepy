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


class FormFactor(MomepyProcessingAlgorithm):
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

    def get_additional_parameters(self):
        return [QgsProcessingParameterField(
            self.HEIGHT_FIELD,
            "Height field",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Numeric,
        )]

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("form_factor", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        h = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)
        gdf = qgs_to_gpd(source, attribute_fields=[h])

        return momepy.form_factor(gdf, gdf[h].to_list())

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("fractal_dimension", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.fractal_dimension(qgs_to_gpd(source)).to_list()


class FacadeRatio(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("facade_ratio", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.facade_ratio(qgs_to_gpd(source)).to_list()


class CircularCompactness(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("circular_compactness", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.circular_compactness(qgs_to_gpd(source)).to_list()


class SquareCompactness(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("square_compactness", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.square_compactness(qgs_to_gpd(source)).to_list()


class Convexity(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("convexity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.convexity(qgs_to_gpd(source)).to_list()


class CourtyardIndex(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("courtyard_index", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.courtyard_index(qgs_to_gpd(source)).to_list()


class Rectangularity(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("rectangularity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.rectangularity(qgs_to_gpd(source)).to_list()


class ShapeIndex(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("shape_index", QMetaType.Type.Double)]
    
    def calculate_values(self, source, parameters, context):
        return momepy.shape_index(qgs_to_gpd(source)).to_list()


class Corners(MomepyProcessingAlgorithm):
    EPS = "EPS"
    INCLUDE_INTERIORS = "INCLUDE_INTERIORS"

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

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterNumber(self.EPS, "Angle threshold (degrees)", QgsProcessingParameterNumber.Double, defaultValue=10),
            QgsProcessingParameterBoolean(self.INCLUDE_INTERIORS, "Include interior rings", defaultValue=False),
        ]
    
    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("corners", QMetaType.Type.Int)]
    
    def calculate_values(self, source, parameters, context):
        return momepy.corners(
            qgs_to_gpd(source),
            eps=self.parameterAsDouble(parameters, self.EPS, context),
            include_interiors=self.parameterAsBool(parameters, self.INCLUDE_INTERIORS, context),
        ).to_list()


class Squareness(MomepyProcessingAlgorithm):
    EPS = "EPS"
    INCLUDE_INTERIORS = "INCLUDE_INTERIORS"

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

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterNumber(self.EPS, "Angle threshold (degrees)", QgsProcessingParameterNumber.Double, defaultValue=10),
            QgsProcessingParameterBoolean(self.INCLUDE_INTERIORS, "Include interior rings", defaultValue=False),
        ]
    
    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("squareness", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.squareness(
            qgs_to_gpd(source),
            eps=self.parameterAsDouble(parameters, self.EPS, context),
            include_interiors=self.parameterAsBool(parameters, self.INCLUDE_INTERIORS, context),
        ).to_list()


class EquivalentRectangularIndex(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("equivalent_rectangular_index", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.equivalent_rectangular_index(qgs_to_gpd(source)).to_list()


class Elongation(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("elongation", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.elongation(qgs_to_gpd(source)).to_list()


class CentroidCornerDistance(MomepyProcessingAlgorithm):
    EPS = "EPS"
    INCLUDE_INTERIORS = "INCLUDE_INTERIORS"

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

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterNumber(self.EPS, "Angle threshold (degrees)", QgsProcessingParameterNumber.Double, defaultValue=10),
            QgsProcessingParameterBoolean(self.INCLUDE_INTERIORS, "Include interior rings", defaultValue=False),
        ]
    
    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("ccd_mean", QMetaType.Type.Double), QgsField("ccd_std", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        result = momepy.centroid_corner_distance(
            qgs_to_gpd(source),
            eps=self.parameterAsDouble(parameters, self.EPS, context),
            include_interiors=self.parameterAsBool(parameters, self.INCLUDE_INTERIORS, context),
        )
        return list(result[["mean", "std"]].itertuples(index=False, name=None))


class Linearity(MomepyProcessingAlgorithm):

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

    def input_geometry_types(self):
        return [Qgis.ProcessingSourceType.VectorLine]

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("linearity", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.linearity(qgs_to_gpd(source)).to_list()

class CompactnessWeightedAxis(MomepyProcessingAlgorithm):

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

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("compactness_weighted_axis", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context):
        return momepy.compactness_weighted_axis(qgs_to_gpd(source)).to_list()


class SunlightOptimised(MomepyProcessingAlgorithm):
    FR_RATIO = "FR_RATIO"
    ELONGATION_RATIO = "ELONGATION_RATIO"
    MIN_COURTYARD_AREA = "MIN_COURTYARD_AREA"

    def name(self):
        return "sunlight_optimised"

    def displayName(self):
        return "Sunlight optimised"

    def group(self):
        return "Shape"

    def groupId(self):
        return "shape"

    def shortHelpString(self):
        return "Whether each building structure is optimised for sunlight (graph-based)."

    def get_additional_parameters(self):
        return [
            QgsProcessingParameterNumber(self.FR_RATIO, "Max area-perimeter ratio", QgsProcessingParameterNumber.Double, defaultValue=8),
            QgsProcessingParameterNumber(self.ELONGATION_RATIO, "Max elongation ratio", QgsProcessingParameterNumber.Double, defaultValue=0.9),
            QgsProcessingParameterNumber(self.MIN_COURTYARD_AREA, "Min courtyard area", QgsProcessingParameterNumber.Double, defaultValue=1),
        ]

    def get_output_fields(self, parameters=None, context=None):
        return [QgsField("sunlight_optimised", QMetaType.Type.Bool)]

    def calculate_values(self, source, parameters, context):
        gdf = qgs_to_gpd(source)
        return momepy.sunlight_optimised(
            gdf,
            self._contiguity_graph(gdf),
            fr_ratio=self.parameterAsDouble(parameters, self.FR_RATIO, context),
            elongation_ratio=self.parameterAsDouble(parameters, self.ELONGATION_RATIO, context),
            min_courtyard_area=self.parameterAsDouble(parameters, self.MIN_COURTYARD_AREA, context),
        ).to_list()
