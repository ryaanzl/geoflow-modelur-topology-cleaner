import os
import geopandas as gpd
from topology import explodeHoles


def saveOutputs(gdf: gpd.GeoDataFrame, inputPath: str, fileName: str,
                geoflowDir: str, modelurDir: str,
                geoflowCrs: int, modelurCrs: int) -> None:
    """
    Save cleaned GeoDataFrame to Geoflow and Modelur formats.
    """

    # Rename reserved columns
    if "fid" in gdf.columns:
        gdf = gdf.rename(columns={"fid": "fidSrc"})
    if "FID" in gdf.columns:
        gdf = gdf.rename(columns={"FID": "fidSrc"})

    # Normalize file naming
    fileBase = os.path.splitext(os.path.basename(inputPath))[0].replace("-", "_")
    subgrid = "_".join(fileBase.split("_")[0:3])

    # Define output paths
    pathGeoflow = os.path.join(geoflowDir, f"{subgrid}_Geoflow.gpkg")
    pathModelur = os.path.join(modelurDir, f"{subgrid}_Modelur.geojson")

    # Export Geoflow
    gdf.to_crs(epsg=geoflowCrs).to_file(pathGeoflow, driver="GPKG")

    # Export Modelur with holes handled
    gdfModelur = gdf.to_crs(epsg=modelurCrs).copy()
    # gdfModelur["geometry"] = gdfModelur["geometry"].apply(explodeHoles)
    # gdfModelur = gdfModelur.explode(index_parts=False).reset_index(drop=True)
    gdfModelur.to_file(pathModelur, driver="GeoJSON")
