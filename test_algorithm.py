import geopandas as gpd
import numpy as np
import shapely

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)

def to_gdf(layer):
    """Convert QGIS layer to GeoDataFrame"""
    features = []
    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom:
            # Convert QGIS geometry to Shapely geometry
            geom_wkt = geom.asWkt()
            shapely_geom = shapely.wkt.loads(geom_wkt)
            
            features.append({
                'geometry': shapely_geom,
                **{field.name(): feature[field.name()] for field in layer.fields()}
            })
    
    if features:
        return gpd.GeoDataFrame(features, crs=layer.sourceCrs().authid())
    else:
        return gpd.GeoDataFrame()

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
    
class facade_ratio_qgs(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'facade_ratio_qgs'
    
    def displayName(self) -> str:
        return 'Facade ratio QGIS'
    
    def group(self) -> str:
        return 'Testing Algorithms'
    
    def groupId(self) -> str:
        return 'testing_algorithms'
    
    def shortHelpString(self) -> str:
        return 'Calculates facade ratio using QGIS'
    
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
    
        # Create output fields (original fields + new ratio field)
        fields = source.fields()
        fields.append(QgsField('facade_ratio', QVariant.Double))
    
        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs()
        )
    
        # Get features from source
        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0
    
        # Process each feature directly
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                
            # Get geometry and calculate facade ratio directly with QGIS geometry
            geom = feature.geometry()
            area = geom.area()
            perimeter = geom.length()
            
            # Calculate facade ratio (avoid division by zero)
            facade_ratio = area / perimeter if perimeter > 0 else 0.0
            
            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geom)
            
            # Copy attributes and add new ratio
            attributes = feature.attributes()
            attributes.append(facade_ratio)
            output_feature.setAttributes(attributes)
            
            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            
            # Update progress
            feedback.setProgress(int(current * total))
    
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()