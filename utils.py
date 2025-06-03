import geopandas as gpd
import shapely as shp

def to_gdf(layer):
    """Convert QGIS layer to GeoDataFrame"""
    features = []
    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom:
            # Convert QGIS geometry to Shapely geometry
            geom_wkt = geom.asWkt()
            shapely_geom = shp.wkt.loads(geom_wkt)
            
            features.append({
                'geometry': shapely_geom,
                **{field.name(): feature[field.name()] for field in layer.fields()}
            })
    
    if features:
        return gpd.GeoDataFrame(features, crs=layer.sourceCrs().authid())
    else:
        return gpd.GeoDataFrame()