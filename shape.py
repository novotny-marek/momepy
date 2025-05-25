import numpy as np

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
)

class facade_ratio(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'facade_ratio'
    
    def displayName(self) -> str:
        return 'Facade ratio'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the facade ratio of each object given its geometry'
    
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
    
class fractal_dimension(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'fractal_dimension'
    
    def displayName(self) -> str:
        return 'Fractal dimension'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates fractal dimension based on area and perimeter'
    
    def initAlgorithm(self, configuration=None):
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
        fields.append(QgsField('fractal_dimension', QVariant.Double))
    
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
            
            # Calculate fractal dimension
            fractal_dimension = (2 * np.log(perimeter / 4)) / np.log(area)
            
            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geom)
            
            # Copy attributes and add new ratio
            attributes = feature.attributes()
            attributes.append(fractal_dimension)
            output_feature.setAttributes(attributes)
            
            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            
            # Update progress
            feedback.setProgress(int(current * total))
    
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()