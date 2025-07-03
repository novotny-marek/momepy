import momepy

from .utils import qgs_to_gpd
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsFields,
    QgsWkbTypes,
    QgsProcessingParameterField,
)


class BufferedLimit(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    def name(self) -> str:
        return "buffered_limit"
    
    def displayName(self) -> str:
        return "Buffered limit"
    
    def group(self) -> str:
        return "Elements"
    
    def groupId(self) -> str:
        return "elements"
    
    def shortHelpString(self) -> str:
        return "Define a limit for tesselation as a buffer around buildings."
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input layer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Buffered limit")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)

        # Convert QGIS feature to GeoDataFrame and create buffered limit
        geometry_dataframe = qgs_to_gpd(source)
        limit = momepy.buffered_limit(geometry_dataframe)
        
        # Create output fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        
        # Create output sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields, 
            QgsWkbTypes.Polygon,
            source.sourceCrs(),
        )
        
        # Create a new feature with the buffered limit geometry
        feature = QgsFeature()
        feature.setFields(fields)
        
        # Convert the shapely geometry to QgsGeometry
        if limit is not None:
            # Convert shapely geometry to WKT and then to QgsGeometry
            limit_wkt = limit.wkt
            qgs_geometry = QgsGeometry.fromWkt(limit_wkt)
            feature.setGeometry(qgs_geometry)
            feature.setAttribute("id", 1)
            
            # Add the feature to the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
        
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()


class MorphologicalTessellation(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    LIMIT = "LIMIT"

    def name(self) -> str:
        return "morphological_tessellation"
    
    def displayName(self) -> str:
        return "Morphological tessellation"
    
    def group(self) -> str:
        return "Elements"
    
    def groupId(self) -> str:
        return "elements"
    
    def shortHelpString(self) -> str:
        return "Generates morphological tessellation."
    
    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                "Input layer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LIMIT,
                "Limit buffer",
                [QgsProcessing.SourceType.VectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "Morphological tesselation")
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        limit_source = self.parameterAsSource(parameters, self.LIMIT, context)

        # Convert QGIS feature to GeoDataFrame and generate morphological tesselation
        geometry_dataframe = qgs_to_gpd(source)
        limit = qgs_to_gpd(limit_source)
        morphological_tessellation = momepy.morphological_tessellation(geometry_dataframe, clip=limit)

        # Create empty fields (tessellation cells only need geometry)
        fields = QgsFields()
        
        # Create output sink
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Polygon,
            source.sourceCrs(),
        )
        
        # Convert tessellation GeoDataFrame back to QGIS features
        for idx, row in morphological_tessellation.iterrows():
            feature = QgsFeature()
            feature.setFields(fields)
            
            # Set geometry from tessellation cell
            geom_wkt = row.geometry.wkt
            qgs_geometry = QgsGeometry.fromWkt(geom_wkt)
            feature.setGeometry(qgs_geometry)
            
            # Add feature to sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
        
        return {self.OUTPUT: dest_id}
    
    def createInstance(self):
        return self.__class__()
