import geopandas as gpd
from config import decimalPrecision, minArea, targetCrs, inputCrsFallback
from topology import (
    roundGeometryCoordsUtm,
    fixInvalidGeometries,
    removeDuplicateVertices,
    enforceOrientation,
    detectOverlaps,
)

def cleanGeodata(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Clean and validate a GeoDataFrame.
    """

    gdf = gdf.copy()

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=inputCrsFallback)

    gdf = gdf.to_crs(epsg=targetCrs)

    gdf["geometry"] = gdf["geometry"].apply(
        lambda geom: roundGeometryCoordsUtm(geom, decimalPrecision) if geom else geom
    )

    gdf = fixInvalidGeometries(gdf)
    gdf = removeDuplicateVertices(gdf)
    gdf = enforceOrientation(gdf)

    gdf["issues"] = ""
    gdf.loc[gdf["geometry"].isnull(), "issues"] += "INVALID_RING;"

    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()]

    gdf = gdf.explode(index_parts=False).reset_index(drop=True)

    gdf["area"] = gdf.geometry.area
    gdf.loc[gdf["area"] < minArea, "issues"] += "SMALL_AREA;"

    gdf = detectOverlaps(gdf)
    gdf.loc[gdf["overlap"], "issues"] += "OVERLAP;"

    return gdf[gdf.geometry.area >= minArea].copy()