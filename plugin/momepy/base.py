import math

from typing import List, Union, Sequence
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsProcessingContext,
    QgsProcessingFeedback,
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

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        """Return the output fields to be added to the output."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_output_fields()"
        )

    def calculate_values(self, source, parameters, context) -> Sequence[Union[float, int, Sequence]]:
        """Calculate the momepy values for the input features."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement calculate_values()"
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def input_layer_name(self) -> str:
        return "Input geometry layer"

    def get_additional_parameters(self) -> List:
        """Return additional parameters specific for this algorithm. Override this if algorithm needs extra parameters."""
        return []

    def initAlgorithm(self, configuration=None):
        """Initialize algorithm with input/output plus additional parameters."""
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.input_layer_name(),
                self.input_geometry_types(),
            )
        )

        # Add algorithm-specific parameters
        for param in self.get_additional_parameters():
            self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.displayName())
        )

    def processAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        """Standard processing algorithm implementation."""
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Create output fields
        fields = source.fields()
        existing = {f.name() for f in fields}
        for field in self.get_output_fields(parameters, context):
            name = field.name()
            if name in existing:
                i = 1
                while f"{name}_{i}" in existing:
                    i += 1
                field.setName(f"{name}_{i}")
                feedback.pushInfo(f"Field '{name}' exists; writing as '{field.name()}'")
            existing.add(field.name())
            fields.append(field)

        # Calculate values using the specific algorithm implementation
        calculated = self.calculate_values(source, parameters, context)

        count = source.featureCount()
        if count >= 0 and len(calculated) != count:
            raise QgsProcessingException(
                f"calculate_values returned {len(calculated)} values for "
                f"{count} features — qgs_to_gpd likely dropped rows (NULL "
                f"geometries?) or momepy output is misaligned."
            )

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
        self._process_features(source, sink, calculated, fields, feedback)

        return {self.OUTPUT: dest_id}

    def _process_features(self, source, sink, calculated, fields, feedback):
        """Process features and add calculated values."""
        count = source.featureCount()
        total = 100.0 / count if count > 0 else 0

        for current, (feature, values) in enumerate(
            zip(source.getFeatures(), calculated)
        ):
            if feedback.isCanceled():
                break

            # Create output feature
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(feature.geometry())

            # Copy attributes and add new calculated values
            attrs = feature.attributes()

            if not isinstance(values, (list, tuple)):
                values = [values]

            attrs.extend(
                None if isinstance(v, float) and math.isnan(v) else v for v in values
            )
            output_feature.setAttributes(attrs)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

    def createInstance(self):
        return self.__class__()

class MomepyGeometryAlgorithm(QgsProcessingAlgorithm):
    """Baseclass for momepy algorithms producing new geometry layer"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def run_momepy(self, gdf, parameters, context):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run_momepy()"
        )

    def output_fields(self) -> List:
        return []

    def output_wkb_type(self, source) -> int:
        return source.wkbType()

    def processAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        gdf = qgs_to_gpd(source)

        result = self.run_momepy(gdf, parameters, context)

        fields = self.output_fields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            self.output_wkb_type(source),
            source.sourceCrs(),
        )

        geoms = result.geometry if hasattr(result, "geometry") else result

        total = 100.0 / len(geoms) if len(geoms) else 0
        for current, geom in enumerate(geoms):
            if feedback.isCanceled():
                break
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(QgsGeometry.fromWkb(bytes(geom.wkb)))
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()
