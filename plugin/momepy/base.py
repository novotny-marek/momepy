from typing import List, Union
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)


class MomepyProcessingAlgorithm(QgsProcessingAlgorithm):
    """Base class for momepy processing algorithms."""

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def __init__(self):
        super().__init__()

    def get_output_fields(self) -> List[QgsField]:
        """Return the output fields to be added to the output."""
        pass

    def calculate_values(self, source, parameters, context) -> List[Union[float, int]]:
        """Calculate the momepy values for the input features."""
        pass

    def get_additional_parameters(self) -> List:
        """Return additional parameters specific for this algorithm. Override this if algorithm needs extra parameters."""
        return []

    def initAlgorithm(self, configuratio=None):
        """Initialize algorithm with input/output plus additional parameters."""
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input geometry layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            )
        )

        # Add algorithm-specific parameters
        for param in self.get_additional_parameters():
            self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.displayName())
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Standard processing algorithm implementation."""
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Calculate values using the specific algorithm implementation
        calculated_values = self.calculate_values(source, parameters, context)

        # Create output fields
        fields = source.fields()
        for field in self.get_output_fields():
            fields.append(field)

        # Create sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs(),
        )

        # Process features
        self._process_features(source, sink, calculated_values, fields, feedback)

        return {self.OUTPUT: dest_id}

    def _process_features(self, source, sink, calculated_values, fields, feedback):
        """Process features and add calculated values."""
        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new calculated values
            attributes = feature.attributes()

            # Handle single values or multiple values
            if isinstance(calculated_values[current], (list, tuple)):
                attributes.extend(calculated_values[current])
            else:
                attributes.append(calculated_values[current])

            output_feature.setAttributes(attributes)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

    def createInstance(self):
        return self.__class__()
