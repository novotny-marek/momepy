import geopandas as gpd
import shapely as shp


def qgs_to_gpd(source, attribute_fields=None):
    """
    Convert QGIS feature soure to Geopandas GeoSeries

    Parameters:
    -----------
    source : QgsProcessingParameterFeatureSource
        QGIS feature source
    attribute_fields : list or None
        List of field names to extract as attributes
        If None, returns only GeoSeries
        If list, returns GeoDataFrame with specified fields

    Returns:
    --------
    gpd.GeoSeries or gpd.GeoDataFrame
    """
    geometries = []
    attributes_data = {}

    # Initialize attribute dictionary if needed
    if attribute_fields:
        for field_name in attribute_fields:
            attributes_data[field_name] = []

    # Extract data from features
    for feature in source.getFeatures():
        # Extract geometries
        qgs_geometry = feature.geometry()
        wkt = qgs_geometry.asWkt()
        shapely_geometry = shp.from_wkt(wkt)
        geometries.append(shapely_geometry)

        # Extract attributes if needed
        if attribute_fields:
            field_names = [field.name() for field in source.fields()]
            feature_attributes = feature.attributes()

            for field_name in attribute_fields:
                if field_name in field_names:
                    field_index = field_names.index(field_name)
                    value = feature_attributes[field_index]
                    attributes_data[field_name].append(value)
                else:
                    # Field not found, add None
                    attributes_data[field_name].append(None)

    # Create appropriate return type
    if attribute_fields:
        # Create GeoDataFrame with attributes
        gdf_data = attributes_data.copy()
        gdf_data["geometry"] = geometries
        return gpd.GeoDataFrame(gdf_data)
    else:
        # Return just GeoSeries
        return gpd.GeoSeries(geometries)
