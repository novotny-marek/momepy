import geopandas as gpd
import numpy as np

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)

def to_gdf(layer):
    return gpd.GeoDataFrame(layer)

class test_algorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'testing_algorithm'
    
    def displayName(self) -> str:
        return 'Testing Algorithm'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'This is a testing algorithm.'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input layer',
                [QgsProcessing.SourceType.TypeVectorAnyGeometry],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output Layer')
        )

    def processAlgorithm(
            self,
            parameters,
            context,
            feedback,
    ):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs(),
        )

        features = source.getFeatures()

        for _, feature in enumerate(features):
            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class facade_ratio(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'facade_ratio'
    
    def displayName(self) -> str:
        return 'Facade ratio'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'Calculates facade ratio'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processingAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        geometry = to_gdf(source)

        geometry['facade_ratio'] = geometry.area / geometry.length

        fields = source.fields()
        fields.append(QgsField('facade_ratio', QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            fields,
            source.wkbType(),
            source.sourceCrs()
        )

        features = source.getFeatures()

        for current, feature in enumerate(features):
            ratio = gdf.loc[feature.id(), 'facade_ratio']

            output_feature = feature
            output_feature.setFields(fields)
            attributes = feature.attributes()
            attributes.append(ratio)
            output_feature.setAttributes(attributes)

            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()