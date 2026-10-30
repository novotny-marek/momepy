import math

from typing import List, Union, Sequence, Tuple
from qgis.core import (
    Qgis,
    QgsField,
    QgsFeature,
    QgsFeatureSink,
    QgsFields,
    QgsGeometry,
    QgsProcessingException,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
)
from .utils import qgs_to_gpd


class MomeQProcessingAlgorithm(QgsProcessingAlgorithm):
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

            attrs.extend(_to_qgis_value(v) for v in values)
            output_feature.setAttributes(attrs)

            # Add feature to sink
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)

            # Update progress
            feedback.setProgress(int(current * total))

    def createInstance(self):
        return self.__class__()

def _to_qgis_value(v):
    """Normalise a Python/numpy scalar for QgsFeature.setAttributes()."""
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, "item"):  # numpy scalar -> native Python type
        return v.item()
    return v


def shapely_to_qgs_geometry(geom) -> QgsGeometry:
    """Convert a shapely geometry to a QgsGeometry.

    QgsGeometry.fromWkb() is an *instance* method in PyQGIS (unlike the
    static fromWkt()), so it cannot be called on the class. QGIS 4 provides
    the direct static converter QgsGeometry.from_shapely(); fall back to the
    instance-based fromWkb() pattern on older bindings.
    """
    if hasattr(QgsGeometry, "from_shapely"):
        return QgsGeometry.from_shapely(geom)
    qgs_geom = QgsGeometry()
    qgs_geom.fromWkb(bytes(geom.wkb))
    return qgs_geom


class MomeQGeometryAlgorithm(QgsProcessingAlgorithm):
    """Baseclass for momepy algorithms producing new geometry layer"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def input_geometry_types(self):
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def input_layer_name(self):
        return "Input geometry layer"

    def get_additional_parameters(self):
        return []

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.input_layer_name(),
                self.input_geometry_types(),
            )
        )
        for param in self.get_additional_parameters():
            self.addParameter(param)
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, self.displayName())
        )

    def run_momepy(self, gdf, parameters, context):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run_momepy()"
        )

    def output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return []

    def row_attributes(self, index, row) -> List:
        """Attributes for one output row; only used when output_fields() is non-empty."""
        return []

    def output_wkb_type(self, source) -> int:
        return source.wkbType()

    def processAlgorithm(
        self, parameters, context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        gdf = qgs_to_gpd(source)

        result = self.run_momepy(gdf, parameters, context)

        # parameterAsSink() requires a QgsFields instance, not a Python list.
        fields = QgsFields()
        for field in self.output_fields(parameters, context):
            fields.append(field)

        # Convert the result to QgsGeometry objects up-front so the sink can be
        # created with the *actual* geometry type. QGIS memory sinks
        # (TEMPORARY_OUTPUT) cannot be created with Qgis.WkbType.Unknown.
        if hasattr(result, "iterrows") and hasattr(result, "columns"):
            # GeoDataFrame-like result
            geom_col = result.geometry.name
            items = list(result.iterrows())
            geometries = [
                shapely_to_qgs_geometry(row[geom_col]) for _, row in items
            ]
        else:
            # Plain iterable of shapely geometries.
            geoms = result.geometry if hasattr(result, "geometry") else result
            geoms = list(geoms)
            items = [(i, None) for i in range(len(geoms))]
            geometries = [shapely_to_qgs_geometry(g) for g in geoms]

        wkb_type = self.output_wkb_type(source)
        if wkb_type == Qgis.WkbType.Unknown:
            wkb_type = (
                geometries[0].wkbType()
                if geometries
                else Qgis.WkbType.NoGeometry
            )

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            wkb_type,
            source.sourceCrs(),
        )

        has_attrs = fields.count() > 0

        total = 100.0 / len(geometries) if geometries else 0
        for current, ((index, row), geometry) in enumerate(zip(items, geometries)):
            if feedback.isCanceled():
                break
            output_feature = QgsFeature(fields)
            output_feature.setGeometry(geometry)
            if has_attrs:
                output_feature.setAttributes(
                    [_to_qgis_value(v) for v in self.row_attributes(index, row)]
                )
            sink.addFeature(output_feature, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()
