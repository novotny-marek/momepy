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
    wkbs = []
    attributes_data = {}
    crs = source.sourceCrs().geographicCrsAuthId()

    # Initialize attribute dictionary if needed
    if attribute_fields:
        for field_name in attribute_fields:
            attributes_data[field_name] = []

    # Extract data from features
    for feature in source.getFeatures():
        # Extract geometries
        qgs_geometry = feature.geometry()
        wkb = bytes(qgs_geometry.asWkb())
        wkbs.append(wkb)

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

    geometries = shp.from_wkb(wkbs)

    # Create appropriate return type
    if attribute_fields:
        # Create GeoDataFrame with attributes
        return gpd.GeoDataFrame(attributes_data, geometry=geometries, crs=crs)
    else:
        # Return just GeoSeries
        return gpd.GeoSeries(geometries, crs=crs)
