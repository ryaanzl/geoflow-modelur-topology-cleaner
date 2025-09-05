"""
Main entry point for the geodata cleaning and export pipeline.

Author: Ryan Zulqifli
Contact: ryanzulqifli@gmail.com
"""

import os
import re
import warnings
from datetime import datetime

import geopandas as gpd
from alive_progress import alive_bar
from colorama import Fore, Style, init

from config import geoflowCrs, modelurCrs
from cleanGeodata import cleanGeodata
from export import saveOutputs

# Initialize colorama
init(autoreset=True)

# Suppress specific warnings
warnings.filterwarnings("ignore", "Several features with id", RuntimeWarning)
warnings.filterwarnings("ignore", "GeoSeries.notna", UserWarning)

# ANSI 256-color codes
tan = "\033[38;5;180m"
peru = "\033[38;5;173m"
steelblue = "\033[38;5;67m"
reset = "\033[0m"

# User configuration
baseDir = r"C:\3D_RYAN\03 PROJECT\02 TOPOLOGI\MOLK\2025_09_04\tes"
folderData = "DATA"
processMode = "ro"  # Options: "ro", "bo", "kanopi"

# Output directories
todayStr = datetime.today().strftime("%Y_%m_%d")
baseOutputDir = os.path.join(baseDir, f"OUTPUT_{todayStr}")
geoflowDir = os.path.join(baseOutputDir, "GEOFLOW")
modelurDir = os.path.join(baseOutputDir, "MODELUR")

os.makedirs(geoflowDir, exist_ok=True)
os.makedirs(modelurDir, exist_ok=True)

# Main execution
if __name__ == "__main__":
    filesToProcess = []
    pattern = re.compile(r"^[A-Z]{2}_\d{2}_[A-Z]")
    dataDir = os.path.join(baseDir, folderData)

    # Locate matching files
    if not os.path.exists(dataDir):
        print(f"{peru}⚠ Missing folder: {dataDir}{reset}")
    else:
        for root, _, files in os.walk(dataDir):
            if not files:
                continue

            normalized = [f.replace("-", "_") for f in files]
            matched = [
                orig for orig, chk in zip(files, normalized)
                if chk.lower().endswith(".geojson")
                and pattern.search(chk)
                and processMode in chk.lower()
            ]
            for f in matched:
                filesToProcess.append(os.path.join(root, f))

    print(
        f"\n{tan}Total matching geojson with '{processMode.upper()}': "
        f"{peru}{len(filesToProcess)} Grid{reset}"
    )

    with alive_bar(
        len(filesToProcess),
        bar="filling",
        spinner="waves",
        title=f"{tan}Processing {processMode} files{reset}",
        force_tty=True,
        enrich_print=False,
        theme="smooth"
    ) as bar:
        for inputPath in filesToProcess:
            fileName = os.path.splitext(os.path.basename(inputPath))[0]
            fileBase = fileName.replace("-", "_")
            subgrid = "_".join(fileBase.split("_")[0:3])

            bar.title = (
                f"{tan}Processing {processMode.upper()} files:{reset} "
                f"{peru}{subgrid}{reset}"
            )

            try:
                gdf = gpd.read_file(inputPath)
                gdfClean = cleanGeodata(gdf)
                saveOutputs(
                    gdfClean, inputPath, fileName,
                    geoflowDir, modelurDir,
                    geoflowCrs, modelurCrs
                )
            except Exception as e:
                bar.text(f"{peru}Failed {inputPath}{reset} | Error: {e}")

            bar()

    print(
        f"{steelblue}\nProcess completed. "
        f"{Fore.LIGHTBLACK_EX}(cc: ryanzulqifli@gmail.com){Style.RESET_ALL}"
    )