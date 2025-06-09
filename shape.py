import numpy as np
import momepy

from .utils import qgs_to_gpd
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsProcessing,
    QgsFeatureSink,
    QgsGeometry,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
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

        # Convert QGIS source to GeoSeries and calculate facade ratio
        geometry_series = qgs_to_gpd(source)
        facade_ratio_series = momepy.facade_ratio(geometry_series)
        facade_ratio_values = facade_ratio_series.to_list()
    
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
            
            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())
            
            # Copy attributes and add new ratio
            attributes = feature.attributes()
            attributes.append(facade_ratio_values[current])
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

        # Convert QGIS source to GeoDataFrame and calculate fractal dimension
        geometry_series = qgs_to_gpd(source)
        fractal_dimension_series = momepy.fractal_dimension(geometry_series)
        fractal_dimension_values = fractal_dimension_series.to_list()
    
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
                         
            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())
            
            # Copy attributes and add new ratio
            attributes = feature.attributes()
            attributes.append(fractal_dimension_values[current])
            output_feature.setAttributes(attributes)
            
            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            
            # Update progress
            feedback.setProgress(int(current * total))
    
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class square_compactness(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FIELD_NAME = 'FIELD_NAME'

    def name(self) -> str:
        return 'square_compactness'
    
    def displayName(self) -> str:
        return 'Square compactness'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the square compactness of each object given its geometry'
    
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

        # Convert QGIS source to GeoDataFrame and calculate square compactness
        geometry_series = qgs_to_gpd(source)
        square_compactness_series = momepy.square_compactness(geometry_series)
        square_compactness_values = square_compactness_series.to_list()
    
        # Create output fields (original fields + new ratio field)
        fields = source.fields()
        fields.append(QgsField('square_compactness', QVariant.Double))
    
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

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())
            
            # Copy attributes and add new ratio
            attributes = feature.attributes()
            attributes.append(square_compactness_values[current])
            output_feature.setAttributes(attributes)
            
            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            
            # Update progress
            feedback.setProgress(int(current * total))
    
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class form_factor(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    HEIGHT_FIELD = 'HEIGHT_FIELD'

    def name(self) -> str:
        return 'form_factor'
    
    def displayName(self) -> str:
        return 'Form factor'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the form factor of each object given its geometry and height'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                'Height field',
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        height_field = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)

        # Create output fields (original fields + new form factor field)
        fields = source.fields()
        fields.append(QgsField('form_factor', QVariant.Double))

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

            geom = feature.geometry()
            area = geom.area()
            perimeter = geom.length()

            # Get height from field
            height = feature[height_field]

            # Calculate form factor
            if height is None or height <= 0 or area <= 0:
                form_factor_value = None
            else:
                volume = area * height
                surface = (perimeter * height) + area
                form_factor_value = surface / (volume ** (2 / 3)) if volume > 0 else None
            
            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geom)

            # Copy attributes and add new form factor
            attributes = feature.attributes()
            attributes.append(form_factor_value)
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class circular_compactness(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'circular_compactness'
    
    def displayName(self) -> str:
        return 'Circular compactness'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculated the circular compactness of each object given its geometry'
    
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

        # Create output fields (original fields + new circular compactness field)
        fields = source.fields()
        fields.append(QgsField('circular_compactness', QVariant.Double))

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

            geom = feature.geometry()
            area = geom.area()

            # Calculate circular compactness
            circle_geom, circle_center, circle_radius = geom.minimalEnclosingCircle()

            if circle_radius > 0:
                circular_compactness = area / (np.pi * circle_radius ** 2)
            else:
                circular_compactness = 0

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geom)

            # Copy attributes and add new circular compactness
            attributes = feature.attributes()
            attributes.append(circular_compactness)
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class convexity(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'convexity'
    
    def displayName(self) -> str:
        return 'Convexity'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the convexity of each object given its geometry'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        fields = source.fields()
        fields.append(QgsField('convexity', QVariant.Double))

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

            geom = feature.geometry()
            area = geom.area()
            hull_area = geom.convexHull().area()

            # Calculate convexity
            convexity = area / hull_area

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geom)

            # Copy attributes and add new convexity
            attributes = feature.attributes()
            attributes.append(convexity)
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()