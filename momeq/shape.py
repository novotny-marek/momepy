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
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean
)

class facade_ratio(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

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

        # Convert QGIS source to GeoSeries and calculate fractal dimension
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

        # Convert QGIS source to GeoSeries and calculate square compactness
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

        # Convert QGIS feature to GeoDataFrame and calculate form factor
        geometry_dataframe = qgs_to_gpd(source, attribute_fields=[height_field])
        height = geometry_dataframe[height_field]
        form_factor_series = momepy.form_factor(geometry_dataframe, height)
        form_factor_values = form_factor_series.to_list()

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
        return 'Calculates the circular compactness of each object given its geometry'
    
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

        # Convert QGIS feature to GeoSeries and calculate circular compactness
        geometry_series = qgs_to_gpd(source)
        circular_compactness_series = momepy.circular_compactness(geometry_series)
        circular_compactness_values = circular_compactness_series.to_list()


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

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new circular compactness
            attributes = feature.attributes()
            attributes.append(circular_compactness_values[current])
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

        # Convert QGIS feature to GeoSeries and calculate convexity
        geometry_series = qgs_to_gpd(source)
        convexity_series = momepy.convexity(geometry_series)
        convexity_values = convexity_series.to_list()

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

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new convexity
            attributes = feature.attributes()
            attributes.append(convexity_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class rectangularity(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'rectangularity'
    
    def displayName(self) -> str:
        return 'Rectangularity'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the rectangularity of each object given its geometry'
    
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

        # Convert QGIS feature to GeoSeries and calculate rectangularity
        geometry_series = qgs_to_gpd(source)
        rectangularity_series = momepy.rectangularity(geometry_series)
        rectangularity_values = rectangularity_series.to_list()

        fields = source.fields()
        fields.append(QgsField('rectangularity', QVariant.Double))

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

            # Copy attributes and add new rectangularity
            attributes = feature.attributes()
            attributes.append(rectangularity_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class corners(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    EPS_FIELD = 'EPS_FIELD'
    INTERIORS_FIELD = 'INTERIORS_FIELD'

    def name(self) -> str:
        return 'corners'
    
    def displayName(self) -> str:
        return 'Corners'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the number of corners of each object given its geometry'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                'Deviation from 180 degrees to consider a corner, by default 10',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                'Include polygon interiors, by default False',
                defaultValue=False,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(parameters, self.INTERIORS_FIELD, context)

        # Convert QGIS feature to GeoSeries and calculate number of corners
        geometry_series = qgs_to_gpd(source)
        corners_series = momepy.corners(geometry_series, eps = eps_field, include_interiors = interiors_field)
        corners_values = corners_series.to_list()

        fields = source.fields()
        fields.append(QgsField('corners', QVariant.Int))

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
    
class squareness(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    EPS_FIELD = 'EPS_FIELD'
    INTERIORS_FIELD = 'INTERIORS_FIELD'

    def name(self) -> str:
        return 'squareness'
    
    def displayName(self) -> str:
        return 'Squareness'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the squareness of each object given its geometry'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                'Deviation from 180 degrees to consider a corner, by default 10',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                'Include polygon interiors, by default False',
                defaultValue=False,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(parameters, self.INTERIORS_FIELD, context)

        # Convert QGIS feature to GeoSeries and calculate squareness
        geometry_series = qgs_to_gpd(source)
        squareness_series = momepy.squareness(geometry_series, eps = eps_field, include_interiors = interiors_field)
        squareness_values = squareness_series.to_list()

        fields = source.fields()
        fields.append(QgsField('squareness', QVariant.Double))

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
    
class equivalent_rectangular_index(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'equivalent_rectangular_index'
    
    def displayName(self) -> str:
        return 'Equivalent rectangular index'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the equivalent rectangular index of each object given its geometry'
    
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

        # Convert QGIS feature to GeoSeries and calculate equivalent rectangular index
        geometry_series = qgs_to_gpd(source)
        eri_series = momepy.equivalent_rectangular_index(geometry_series)
        eri_values = eri_series.to_list()

        fields = source.fields()
        fields.append(QgsField('eri', QVariant.Double))

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

            # Copy attributes and add new equivalent rectangular index
            attributes = feature.attributes()
            attributes.append(eri_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class elongation(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'elongation'
    
    def displayName(self) -> str:
        return 'Elongation'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the elongation of each object given its geometry'
    
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

        # Convert QGIS feature to GeoSeries and calculate elongation
        geometry_series = qgs_to_gpd(source)
        elongation_series = momepy.elongation(geometry_series)
        elongation_values = elongation_series.to_list()

        fields = source.fields()
        fields.append(QgsField('elongation', QVariant.Double))

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

            # Copy attributes and add new elongation
            attributes = feature.attributes()
            attributes.append(elongation_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
    
class centroid_corner_distance(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    EPS_FIELD = 'EPS_FIELD'
    INTERIORS_FIELD = 'INTERIORS_FIELD'

    def name(self) -> str:
        return 'centroid_corner_distance'
    
    def displayName(self) -> str:
        return 'Centroid corner distance'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the centroid corner distance of each object given its geometry'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Layer',
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EPS_FIELD,
                'Deviation from 180 degrees to consider a corner, by default 10',
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INTERIORS_FIELD,
                'Include polygon interiors, by default False',
                defaultValue=False,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        eps_field = self.parameterAsDouble(parameters, self.EPS_FIELD, context)
        interiors_field = self.parameterAsBool(parameters, self.INTERIORS_FIELD, context)

        # Convert QGIS feature to GeoSeries and calculate centroid corner distance
        geometry_series = qgs_to_gpd(source)
        ccd_series = momepy.centroid_corner_distance(geometry_series, eps = eps_field, include_interiors = interiors_field)
        ccd_values = ccd_series.to_list()

        fields = source.fields()
        fields.append(QgsField('ccd', QVariant.Double))

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
    
class linearity(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'linearity'
    
    def displayName(self) -> str:
        return 'Linearity'
    
    def group(self) -> str:
        return 'Shape'
    
    def groupId(self) -> str:
        return 'shape'
    
    def shortHelpString(self) -> str:
        return 'Calculates the linearity of each LineString'
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                'Input Layer',
                [QgsProcessing.SourceType.VectorLine],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Output layer')
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Convert QGIS feature to GeoSeries and calculate linearity
        geometry_series = qgs_to_gpd(source)
        linearity_series = momepy.linearity(geometry_series)
        linearity_values = linearity_series.to_list()

        fields = source.fields()
        fields.append(QgsField('linearity', QVariant.Double))

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

            # Copy attributes and add new linearity
            attributes = feature.attributes()
            attributes.append(linearity_values[current])
            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()