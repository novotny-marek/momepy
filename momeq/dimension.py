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

class courtyard_area(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self) -> str:
        return 'courtyard_area'
    
    def displayName(self) -> str:
        return 'Courtyard area'
    
    def group(self) -> str:
        return 'Dimension'
    
    def groupId(self) -> str:
        return 'dimension'
    
    def shortHelpString(self) -> str:
        return 'Calculates area of holes within geometry - area of courtyards.'
    
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

        # Convert QGIS source to GeoSeries and calculate courtyard area
        geometry_series = qgs_to_gpd(source)
        courtyard_area_series = momepy.courtyard_area(geometry_series)
        courtyard_area_values = courtyard_area_series.to_list()
    
        # Create output fields (original fields + new courtyard area field)
        fields = source.fields()
        fields.append(QgsField('courtyard_area', QVariant.Double))
    
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
            attributes.append(courtyard_area_values[current])
            output_feature.setAttributes(attributes)
            
            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            
            # Update progress
            feedback.setProgress(int(current * total))
    
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()