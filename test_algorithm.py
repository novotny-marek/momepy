import geopandas as gpd
import numpy as np
import shapely
import momepy

from PyQt5.QtCore import QVariant
from .utils import (to_gdf, qgs_to_gpd)
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)
    
class facade_ratio_gpd_old(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'facade_ratio_gpd'
    
    def displayName(self) -> str:
        return 'Facade ratio GeoPandas olde version'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'Calculates facade ratio using GeoPandas'
    
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

    def processAlgorithm(self, parameters, context, feedback):
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
            source.wkbType(),
            source.sourceCrs()
        )

        features = source.getFeatures()

        ratio_values = geometry['facade_ratio'].to_list()

        for i, feature in enumerate(features):
            ratio = ratio_values[i]

            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            attributes = feature.attributes()
            attributes.append(ratio)
            output_feature.setAttributes(attributes)

            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class facade_ratio_gpd_new(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'facade_ratio_gpd_new'
    
    def displayName(self) -> str:
        return 'Facade ratio GeoPandas'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'Calculates facade ratio using GeoPandas'
    
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

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        geometry_series = qgs_to_gpd(source)

        facade_ratio_series = momepy.facade_ratio(geometry_series)

        fields = source.fields()
        fields.append(QgsField('facade_ratio', QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs()
        )

        features = source.getFeatures()

        ratio_values = facade_ratio_series.to_list()

        for i, feature in enumerate(features):
            if feedback.isCanceled():
                break

            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            attributes = feature.attributes()
            attributes.append(ratio_values[i])
            output_feature.setAttributes(attributes)

            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()