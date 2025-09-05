# <img src="https://www.svgrepo.com/show/182472/location-maps-and-location.svg" width="35" style="vertical-align:middle"/> Topology Cleaning of Data Preparation for Geoflow & Modelur

<p align="justify">
A Python-based pipeline for <b>cleaning and validating geospatial topologies</b> 
from <b>GeoJSON input</b> before exporting to <b>Geoflow</b> and <b>Modelur</b>.  
The workflow ensures reliable geometries by removing duplicates, fixing invalid shapes, 
rounding coordinates, checking overlaps, and enforcing topology rules.
</p>

---

## <img src="https://www.svgrepo.com/show/181070/route-gps.svg" width="24" style="vertical-align:middle"/> Features

- Automatic scanning of folder structures for GeoJSON inputs.  
- Configurable processing mode: `RO`, `BO`, or `Kanopi`.  
- Geometry cleaning and validation:
    - Coordinate rounding after reprojection to UTM → `roundGeometryCoordsUtm`
    - Removal of duplicate vertices → `cleanRing`, `cleanPolygonDuplicates`, `removeDuplicateVertices`
    - Repair of invalid geometries → `fixInvalidGeometries`
    - Enforce polygon orientation (right-hand rule) → `enforceOrientation`
    - Explode multipolygons and interior holes → `explodeHoles`
    - Area threshold filtering (discard very small geometries) → handled in `cleanGeodata.py`
    - Overlap detection and flagging → `detectOverlaps`
- Export cleaned results into:
  - **Geoflow**: `.gpkg` in UTM CRS.
  - **Modelur**: `.geojson` in WGS84 CRS.

---

## <img src="https://www.svgrepo.com/show/181175/folder-folder.svg" width="24" style="vertical-align:middle"/> Repository Layout
```
├── main.py                           # Main entry point: orchestrates the pipeline
├── config.py                         # Global configuration: CRS, precision, thresholds
├── topology.py                       # Geometry utilities: validation, overlaps, orientation
├── cleanGeodata.py                   # Cleaning pipeline for geospatial data
├── export.py                         # Export utilities for Geoflow and Modelur outputs
├── readme.md                         # Project documentation
├── requirements.txt                  # Library Requirements 
├── baseDir/                          # Input and output root directory
│   ├── DATA/                         # Raw input GeoJSON files
│   │   ├── AX_25_B_RO.geojson        # Example subgrid GeoJSON file
│   │   └── *.geojson*                # Example subgrid GeoJSON file
│   │
│   └── OUTPUT_{date}/                      # Output generated per run (date-stamped)
│       ├── MODELUR/                        # Modelur outputs (.geojson)
│       │   ├── AX_25_B_Modelur.geojson     # Cleaned Modelur GeoJSON
│       │   └── *geojson*.geojson           # Cleaned Modelur GeoJSON
│       │
│       └── GEOFLOW/                        # Geoflow outputs (.gpkg)
│           ├── AX_25_B_Geoflow.gpkg        # Cleaned Geoflow GeoPackage
│           └── *.gpkg                      # Cleaned Geoflow GeoPackage
```
## <img src="https://www.svgrepo.com/show/182434/levels-controls.svg" width="24" style="vertical-align:middle"/> Installation
### 1. Clone this repository:
```bash
git clone https://github.com/ryaanzl/topology-geoflow-modelur.git
cd topology-geoflow-modelur
```

### 2. Create a virtual environment and install dependencies:
```bash
conda create -n <your-env> python=3.11 -y
conda activate <your-env> 
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Dependencies

The pipeline requires the following Python packages (already listed in requirements.txt):

`geopandas`, `shapely`, `pyogrio`, `fiona`, `gdal`, `proj`, `alive-progress`, `colorama`, `tqdm`

## <img src="https://www.svgrepo.com/show/180902/location-location.svg" width="24" style="vertical-align:middle"/> Usage

### 1. Prepare your data folder structure

```
DATA/
├── AX_25_B/                        # Grid folder
│   ├── AX_25_B_RO.geojson          # Input file (RO)
│   ├── AX_25_B_BO.geojson          # Input file (BO)
│   ├── AX_25_B_Kanopi.geojson      # Input file (Kanopi)
│   └── ...
└── ...
```

### 2. Configure base directory and mode in main.py
```
baseDir = r"C:\path\to\ryan"  # Directory project
processMode = "ro"            # or "bo" or "kanopi"
```
### 3. Run the pipeline:
````bash
python main.py
````

### 4. Processing finished:
When processing is complete, the pipeline prints a final confirmation message with colors applied in the terminal:
```python
Total matching geojson with 'RO': 3 Grid
Processing RO files: AK_16_C |████████████████████████████████████████| 3/3 [100%] in 8.1s (0.29/s)
```
### 5. Results will be saved automatically in dated output folders:
````
OUTPUT_YYYY_MM_DD/
├── GEOFLOW/
│   ├── AX_25_B_Geoflow.gpkg
│   └── ...
├── MODELUR/
│   ├── AX_25_B_Modelur.geojson
│   └── ...
````

## <img src="https://www.svgrepo.com/show/180846/briefcase-travel.svg" width="24" style="vertical-align:middle"/> Workflow Summary

The pipeline (main.py) runs sequentially through these stages:

### [1] Scan input directory for GeoJSON files
````
    └─ Filter by mode (RO, BO, or Kanopi)
````
### [2] Clean geometries
````
    └─ Module: cleanGeodata.py
    └─ Steps:
         • Reproject → UTM
         • Round coordinates
         • Validate and repair geometries
         • Remove duplicate vertices
         • Enforce orientation
         • Explode multipolygons and holes
         • Filter by minimum area
         • Detect overlaps and flag issues
````
### [3] Export results
````
    └─ Module: export.py
    └─ Outputs:
         • Geoflow GPKG (UTM)
         • Modelur GeoJSON (WGS84)
````

---

### <img src="https://www.svgrepo.com/show/181069/user-social.svg" width="14" style="vertical-align:middle"/> Author
Developed and maintained by Github [@ryaanzl](https://github.com/ryaanzl)  
<img src="https://www.svgrepo.com/show/180848/attach-tool.svg" width="14" style="vertical-align:middle"/> [ryanzulqifli@gmail.com](mailto:ryanzulqifli@gmail.com)