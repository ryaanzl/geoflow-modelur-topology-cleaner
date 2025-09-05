"""
Topology utilities for geodata cleaning.

Author: Ryan Zulqifli
"""

import math
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import transform
from shapely.validation import make_valid
from shapely.geometry.polygon import orient
from shapely.strtree import STRtree

from config import decimalPrecision, tolerance


def coordsEqual(c1, c2):
    """Check if two coordinates are effectively equal."""
    return math.isclose(c1[0], c2[0], abs_tol=tolerance) and math.isclose(c1[1], c2[1], abs_tol=tolerance)


def cleanRing(coords):
    """Clean a ring by removing duplicates and rounding coordinates."""
    newCoords, prev = [], None
    for pt in coords[:-1]:
        if prev is None or not coordsEqual(pt, prev):
            newCoords.append((round(pt[0], decimalPrecision), round(pt[1], decimalPrecision)))
        prev = pt
    if len(newCoords) >= 3 and not coordsEqual(newCoords[0], newCoords[-1]):
        newCoords.append(newCoords[0])
    return newCoords


def cleanPolygonDuplicates(geom):
    """Remove duplicate vertices in a polygon or multipolygon."""
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type == "Polygon":
        newExterior = cleanRing(geom.exterior.coords)
        if len(newExterior) < 4:
            return None
        newInteriors = [cleanRing(r.coords) for r in geom.interiors if len(cleanRing(r.coords)) >= 4]
        try:
            return Polygon(newExterior, newInteriors)
        except Exception:
            return None
    elif geom.geom_type == "MultiPolygon":
        parts = [cleanPolygonDuplicates(p) for p in geom.geoms]
        return MultiPolygon([p for p in parts if p]) if parts else None
    return geom


def roundGeometryCoordsUtm(geom, precision=decimalPrecision):
    """Round geometry coordinates to fixed precision."""
    if geom is None or geom.is_empty:
        return geom
    return transform(lambda x, y, z=None: ([round(v, precision) for v in x],
                                          [round(v, precision) for v in y]), geom)


def fixInvalidGeometries(gdf):
    """Repair invalid geometries."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].apply(lambda g: make_valid(g) if g and not g.is_valid else g)
    return gdf


def removeDuplicateVertices(gdf):
    """Clean duplicate vertices across the GeoDataFrame."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].apply(cleanPolygonDuplicates)
    return gdf


def enforceOrientation(gdf):
    """Ensure consistent polygon orientation."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].apply(lambda g: orient(g, sign=1.0) if g else g)
    return gdf


def detectOverlaps(gdf):
    """Flag overlapping geometries."""
    geoms = list(gdf.geometry)
    tree = STRtree(geoms)
    flags = [False] * len(geoms)

    if hasattr(tree, "query_bulk"):
        ia, ib = tree.query_bulk(geoms, predicate="intersects")
        pairs = zip(ia, ib)
    else:
        pairs = []
        for i, geom in enumerate(geoms):
            if geom is None or geom.is_empty:
                continue
            for j in tree.query(geom):
                if i != j:
                    pairs.append((i, j))

    for i, j in pairs:
        a, b = geoms[i], geoms[j]
        if not a or not b or a.is_empty or b.is_empty:
            continue
        if a.touches(b):
            continue
        if a.intersects(b):
            flags[i] = True
            flags[j] = True

    gdf["overlap"] = flags
    return gdf


def explodeHoles(geom):
    """Convert holes in polygons into separate parts."""
    if not geom or geom.is_empty:
        return None
    if geom.geom_type == "Polygon":
        if not geom.interiors:
            return geom
        parts = [Polygon(geom.exterior)] + [Polygon(h) for h in geom.interiors]
        return MultiPolygon(parts)
    elif geom.geom_type == "MultiPolygon":
        parts = []
        for p in geom.geoms:
            parts.append(Polygon(p.exterior))
            parts.extend([Polygon(h) for h in p.interiors])
        return MultiPolygon(parts)
    return geom