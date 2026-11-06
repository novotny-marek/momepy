import momepy

from typing import List, Union
from .base import MomeQProcessingAlgorithm
from .utils import qgs_to_gpd, qgs_to_dataframe
from PyQt6.QtCore import QMetaType
from qgis.core import (
    Qgis,
    QgsField,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
)


class Volume(MomeQProcessingAlgorithm):
    HEIGHT_FIELD = "HEIGHT_FIELD"

    def name(self) -> str:
        return "volume"

    def displayName(self) -> str:
        return "Volume"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates the volume of each object given its geometry and height."

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            )
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("volume", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        h = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)
        gdf = qgs_to_gpd(source, attribute_fields=[h])
        area = gdf.area
        height = gdf[h]
        return momepy.volume(area, height).to_list()


class FloorArea(MomeQProcessingAlgorithm):
    HEIGHT_FIELD = "HEIGHT_FIELD"
    FLOOR_FIELD = "FLOOR_FIELD"

    def name(self) -> str:
        return "floor_area"

    def displayName(self) -> str:
        return "Floor area"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates the floor area of each object given its geometry, height and number of floors."

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            ),
            QgsProcessingParameterField(
                self.FLOOR_FIELD,
                "Floor height field (optional)",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
                optional=True,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("floor_area", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        h = self.parameterAsString(parameters, self.HEIGHT_FIELD, context)
        f = self.parameterAsString(parameters, self.FLOOR_FIELD, context)
        gdf = qgs_to_gpd(source, attribute_fields=[h, f] if f else [h])
        area = gdf.area
        height = gdf[h]
        floor_height = gdf[f] if f else None
        return momepy.floor_area(area, height, floor_height).to_list()


class CourtyardArea(MomeQProcessingAlgorithm):
    def name(self) -> str:
        return "courtyard_area"

    def displayName(self) -> str:
        return "Courtyard area"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates area of holes within geometry - area of courtyards."

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("courtyard_area", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        geometry_series = qgs_to_gpd(source)
        return momepy.courtyard_area(geometry_series).to_list()


class LongestAxisLength(MomeQProcessingAlgorithm):
    def name(self) -> str:
        return "longest_axis_length"

    def displayName(self) -> str:
        return "Longest axis length"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return "Calculates the length of the longest axis of object."

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("longest_axis_length", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> List[float]:
        geometry_series = qgs_to_gpd(source)
        return momepy.longest_axis_length(geometry_series).to_list()


class PerimeterWall(MomeQProcessingAlgorithm):
    GRAPH = "GRAPH"

    def name(self) -> str:
        return "perimeter_wall"

    def displayName(self) -> str:
        return "Perimeter wall"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return (
            "Calculates the perimeter of the building wall. "
            "If a graph is provided, it will be used instead of automatically generating one."
        )

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterFeatureSource(
                self.GRAPH,
                "Graph (optional)",
                [Qgis.ProcessingSourceType.Vector],
                optional=True,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        return [QgsField("perimeter_wall", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> list:
        # Get buildings with FID as index for consistency with graph
        field_names = [field.name() for field in source.fields()]
        if 'fid' in field_names:
            gdf = qgs_to_gpd(source, attribute_fields=['fid'])
            gdf = gdf.set_index('fid')
        else:
            gdf = qgs_to_gpd(source)
        
        # Check if graph is provided
        graph_source = self.parameterAsSource(parameters, self.GRAPH, context)
        if graph_source:
            # Convert graph table to libpysal Graph object
            from libpysal.graph import Graph
            
            # Get edge list from graph table (no geometry, use qgs_to_dataframe)
            graph_df = qgs_to_dataframe(graph_source)
            
            # Build adjacency dictionary from edge list
            neighbors = {}
            weights = {}
            
            # Check what columns are available
            cols = list(graph_df.columns)
            
            # Try to find source/target columns (case insensitive)
            source_col = next((c for c in cols if c.lower() in ['source', 'focal', 'origin']), None)
            target_col = next((c for c in cols if c.lower() in ['target', 'neighbor', 'destination']), None)
            weight_col = next((c for c in cols if c.lower() in ['weight', 'cost', 'distance']), None)
            
            if source_col and target_col:
                # Build neighbors and weights from edge list
                for _, row in graph_df.iterrows():
                    source = row[source_col]
                    target = row[target_col]
                    weight_val = row[weight_col] if weight_col else 1.0
                    
                    # Add both directions for undirected graph
                    if source not in neighbors:
                        neighbors[source] = []
                        weights[source] = {}
                    neighbors[source].append(target)
                    weights[source][target] = weight_val
                    
                    # Add reverse direction
                    if target not in neighbors:
                        neighbors[target] = []
                        weights[target] = {}
                    neighbors[target].append(source)
                    weights[target][source] = weight_val
                
                # Ensure all features from geometry are in the graph
                # Even isolated features (with no neighbors) need to be included
                for idx in gdf.index:
                    if idx not in neighbors:
                        neighbors[idx] = []
                        weights[idx] = {}
                
                # Create Graph object from edge list
                # The graph will have FID indices matching the geometry
                graph = Graph.from_dicts(neighbors, weights)
                
                # Pass to momepy - both gdf and graph use FID index
                return momepy.perimeter_wall(gdf, graph).to_list()
        
        # If no graph provided, use default momepy behavior (auto-generate)
        return momepy.perimeter_wall(gdf).to_list()


class StreetProfile(MomeQProcessingAlgorithm):
    INPUT_BUILDINGS = "INPUT_BUILDINGS"
    DISTANCE = "DISTANCE"
    TICK_LENGTH = "TICK_LENGTH"
    HEIGHT_FIELD = "HEIGHT_FIELD"

    def name(self) -> str:
        return "street_profile"

    def displayName(self) -> str:
        return "Street profile"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return (
            "Calculates the street profile characters: width, openness and "
            "width deviation; with a building height field also height, "
            "height deviation and the height/width ratio."
        )

    def input_geometry_types(self) -> List[Qgis.ProcessingSourceType]:
        return [Qgis.ProcessingSourceType.VectorLine]

    def input_layer_name(self) -> str:
        return "Input street network layer"

    def get_additional_parameters(self) -> List[QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterFeatureSource(
                self.INPUT_BUILDINGS,
                "Input buildings layer",
                [Qgis.ProcessingSourceType.VectorPolygon],
            ),
            QgsProcessingParameterNumber(
                self.DISTANCE,
                "The distance between perpendicular ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
            ),
            QgsProcessingParameterNumber(
                self.TICK_LENGTH,
                "The length of ticks.",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=50.0,
            ),
            QgsProcessingParameterField(
                self.HEIGHT_FIELD,
                "Height field",
                parentLayerParameterName=self.INPUT_BUILDINGS,
                type=QgsProcessingParameterField.Numeric,
                defaultValue=None,
                optional=True,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> List[QgsField]:
        fields = [
            QgsField("width", QMetaType.Type.Double),
            QgsField("openness", QMetaType.Type.Double),
            QgsField("width_deviation", QMetaType.Type.Double),
        ]
        if parameters is not None and self.parameterAsString(
            parameters, self.HEIGHT_FIELD, context
        ):
            fields.extend(
                [
                    QgsField("height", QMetaType.Type.Double),
                    QgsField("height_deviation", QMetaType.Type.Double),
                    QgsField("hw_ratio", QMetaType.Type.Double),
                ]
            )
        return fields

    def calculate_values(self, source, parameters, context) -> List:
        building_source = self.parameterAsSource(
            parameters, self.INPUT_BUILDINGS, context
        )
        distance = self.parameterAsDouble(parameters, self.DISTANCE, context)
        tick_length = self.parameterAsDouble(parameters, self.TICK_LENGTH, context)
        height_field = (
            self.parameterAsString(parameters, self.HEIGHT_FIELD, context) or None
        )

        buildings = qgs_to_gpd(building_source, attribute_fields=height_field)
        streets = qgs_to_gpd(source)
        heights = buildings[height_field] if height_field else None

        result = momepy.street_profile(
            streets, buildings, distance, tick_length, heights
        )

        columns = ["width", "openness", "width_deviation"]
        if height_field:
            columns += ["height", "height_deviation", "hw_ratio"]

        return list(zip(*[result[c].to_list() for c in columns]))


class WeightedCharacter(MomeQProcessingAlgorithm):
    CHARACTER_FIELD = "CHARACTER_FIELD"
    GRAPH = "GRAPH"

    def name(self) -> str:
        return "weighted_character"

    def displayName(self) -> str:
        return "Weighted Character"

    def group(self) -> str:
        return "Dimension"

    def groupId(self) -> str:
        return "dimension"

    def shortHelpString(self) -> str:
        return (
            "Calculates the weighted character. Character weighted by the area of the "
            "objects within neighbors defined in a graph. Requires a character field "
            "(e.g., elongation, compactness) and an optional graph input."
        )

    def input_geometry_types(self) -> list:
        return [Qgis.ProcessingSourceType.VectorPolygon]

    def get_additional_parameters(self) -> list:
        return [
            QgsProcessingParameterField(
                self.CHARACTER_FIELD,
                "Character field",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
            ),
            QgsProcessingParameterFeatureSource(
                self.GRAPH,
                "Graph (optional)",
                [Qgis.ProcessingSourceType.Vector],
                optional=True,
            ),
        ]

    def get_output_fields(self, parameters=None, context=None) -> list:
        return [QgsField("weighted_character", QMetaType.Type.Double)]

    def calculate_values(self, source, parameters, context) -> list:
        from libpysal.graph import Graph
        import pandas as pd
        
        # Get character field name
        char_field = self.parameterAsString(parameters, self.CHARACTER_FIELD, context)
        
        # Get geometry and character values with FID as index for consistency
        field_names = [field.name() for field in source.fields()]
        attrs_to_get = [char_field]
        if 'fid' in field_names:
            attrs_to_get.append('fid')
        
        gdf = qgs_to_gpd(source, attribute_fields=attrs_to_get)
        
        if 'fid' in gdf.columns:
            gdf = gdf.set_index('fid')
        
        y = gdf[char_field]
        area = gdf.area

        # Check if graph is provided
        graph_source = self.parameterAsSource(parameters, self.GRAPH, context)
        if graph_source:
            # Convert graph table to libpysal Graph object
            from libpysal.graph import Graph
            
            # Get edge list from graph table (no geometry, use qgs_to_dataframe)
            graph_df = qgs_to_dataframe(graph_source)
            
            # Build adjacency dictionary from edge list
            neighbors = {}
            weights = {}
            
            # Check what columns are available
            cols = list(graph_df.columns)
            
            # Try to find source/target columns (case insensitive)
            source_col = next((c for c in cols if c.lower() in ['source', 'focal', 'origin']), None)
            target_col = next((c for c in cols if c.lower() in ['target', 'neighbor', 'destination']), None)
            weight_col = next((c for c in cols if c.lower() in ['weight', 'cost', 'distance']), None)
            
            if source_col and target_col:
                # Build neighbors and weights from edge list
                for _, row in graph_df.iterrows():
                    source = row[source_col]
                    target = row[target_col]
                    weight_val = row[weight_col] if weight_col else 1.0
                    
                    # Add both directions for undirected graph
                    if source not in neighbors:
                        neighbors[source] = []
                        weights[source] = {}
                    neighbors[source].append(target)
                    weights[source][target] = weight_val
                    
                    # Add reverse direction
                    if target not in neighbors:
                        neighbors[target] = []
                        weights[target] = {}
                    neighbors[target].append(source)
                    weights[target][source] = weight_val
                
                # Ensure all features from geometry are in the graph
                # Even isolated features (with no neighbors) need to be included
                for idx in gdf.index:
                    if idx not in neighbors:
                        neighbors[idx] = []
                        weights[idx] = {}
                
                # Create Graph object from edge list
                graph = Graph.from_dicts(neighbors, weights)
            else:
                # If we can't find the columns, fall back to building contiguity
                graph = None
        else:
            graph = None

        # If no graph provided or graph conversion failed, build contiguity graph
        if graph is None:
            graph = Graph.build_contiguity(gdf)

        # Calculate weighted character
        return momepy.weighted_character(y, area, graph).to_list()
