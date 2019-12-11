"""
generate_time_slice_atlases.py pbf_path geojsons_folder_path timestamp1 timestamp2 atlas_jar country_boundary_map iso_codes

This program is writen in python 3.6.
It create atlases for 2 timestamps and a set of geojson boundaries, from an OSM PBF history file.

Requires the following non-python programs to be installed and callable from the command line:
java
osmium-tool


Created by: Bentley Breithaupt
2019
"""


import argparse
import copy
import json
import logging
import os
import shutil
import subprocess
import time

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

EXTRACT_CONFIG_FILE_PATH = "extract.json"
EXTRACT_PBFS_DIRECTORY_PATH = "extracts/"
TEMP_DIRECTORY_PATH = "temp/"
TIME_SLICES_ONE_DIRECTORY = "time_slices1/"
TIME_SLICES_TWO_DIRECTORY = "time_slices2/"
TIME_SLICES_ONE_CLEAN_DIRECTORY = "time_slices1_clean/"
TIME_SLICES_TWO_CLEAN_DIRECTORY = "time_slices2_clean/"
PBF_EXTENSION = ".pbf"


def sub_run_string(command_string):
    """
    Helper function for using subprocess.run().

    :param command_string: command to run as a single string
    :return: None
    """
    subprocess.run(command_string.split(" "))


def get_args():
    """
    Reads and parses command line arguments.

    :return: a namespace with the program args or defaults
    """
    parser = argparse.ArgumentParser(description="Create atlases for 2 timestamps and a set of geojson boundaries, "
                                                 "from an OSM PBF history file.")
    parser.add_argument("pbf_path", help="path to the OSM PBF history file to extract from")
    parser.add_argument("geojsons_folder_path", help="directory of geojson files to get extracts of")
    parser.add_argument("timestamp1", help="first timestamp to extract; format: yyyy-mm-ddThh:mm:ssZ")
    parser.add_argument("timestamp2", help="second timestamp to extract; format: yyyy-mm-ddThh:mm:ssZ")
    parser.add_argument("atlas_jar", help="Atlas shaded jar file")
    parser.add_argument("country_boundary_map", help="country boundary map to feed to Atlas")
    parser.add_argument("iso_codes", help="ISO country codes from the country boundary map to generate atlases for")
    return parser.parse_args()


def get_files_of_type(directory, file_type):
    """
    Given a directory, return all the path to all the files of the given type.

    :param directory: path to a directory
    :param file_type: the file extension to look for
    :return: a list of string file paths
    """
    files = os.listdir(directory)
    files_of_type = []
    for file in files:
        if file.endswith(file_type):
            files_of_type.append(os.path.join(directory, file))
    return files_of_type


def generate_extracts_config(geojson_paths):
    """
    Generate the area extract configuration, used by Osmium, for a set of geojsons.

    :param geojson_paths: path to the geojson boundary files
    :return: None
    """
    extracts_json = {"directory": EXTRACT_PBFS_DIRECTORY_PATH, "extracts": []}
    extract_json = {"output": "", "multipolygon": {"file_name": "", "file_type": "geojson"}}
    for path in geojson_paths:
        new_extract = copy.deepcopy(extract_json)
        new_extract["multipolygon"]["file_name"] = path
        new_extract["output"] = os.path.split(path)[1][:-8]+".osh.pbf"
        extracts_json["extracts"].append(new_extract)
    with open(EXTRACT_CONFIG_FILE_PATH, "w") as extract_file:
        extract_file.write(json.dumps(extracts_json))


def extract_history_files(pbf_path):
    """
    Cut an OSM history file using the extract configuration made by generate_extracts_config()

    :param pbf_path: path to the OSM PBF history file
    :return: None
    """
    os.mkdir(EXTRACT_PBFS_DIRECTORY_PATH)
    sub_run_string("osmium extract --with-history -c {} {}".format(EXTRACT_CONFIG_FILE_PATH, pbf_path))


def time_slice_pbfs(timestamp, output_directory):
    """
    Time slice all the files created by extract_history_files() by the given timestamp.

    :param timestamp: Timestamp to slice by
    :param output_directory: Directory to output the slices to
    :return: None
    """
    os.mkdir(output_directory)
    for file in get_files_of_type(EXTRACT_PBFS_DIRECTORY_PATH, PBF_EXTENSION):
        LOGGER.info("Slicing {}".format(file))
        sub_run_string("osmium time-filter {} {} -o {}.osm.pbf".format(file, timestamp, output_directory+os.path
                                                                       .split(file)[1][:-8]))


def clean_pbfs(pbf_directory, clean_directory):
    """
    Clean a directory of PBFs, removing any Nodes without spatial information.

    :param pbf_directory: Directory of PBFs to clean
    :param clean_directory: Directory to output the newly cleaned PBFs to
    :return: None
    """
    os.mkdir(TEMP_DIRECTORY_PATH)
    os.mkdir(clean_directory)
    for file in get_files_of_type(pbf_directory, PBF_EXTENSION):
        LOGGER.info("Cleaning {}".format(file))
        osm_file = TEMP_DIRECTORY_PATH+"temp.osm"
        osm_clean_file = TEMP_DIRECTORY_PATH+"temp_clean.osm"
        sub_run_string("osmium cat {} -o {}".format(file, osm_file))
        with open(osm_file) as f:
            with open(osm_clean_file, "w") as o:
                for line in f:
                    if line.find("<node") == -1 or (line.find("lat") != -1 and line.find("lon") != -1):
                        o.write(line)
        sub_run_string("osmium cat {} -o {}{}".format(osm_clean_file, clean_directory, os.path.split(file)[1]))
        os.remove(TEMP_DIRECTORY_PATH+"temp.osm")
        os.remove(TEMP_DIRECTORY_PATH+"temp_clean.osm")
    safe_rm_dir(TEMP_DIRECTORY_PATH)


def generate_atlases(pbf_directory, atlas_jar, country_boundary_map, iso_codes, output_directory):
    """
    Run PBF to Atlas subcommand in Atlas to generate atlases for a set of PBFs.

    :param pbf_directory: PBFs to convert to atlases
    :param atlas_jar: Atlas jar file to run
    :param country_boundary_map: Atlas country boundary map to use
    :param iso_codes: ISO country codes from the country boundary map tp generate atlases for
    :param output_directory: Directory to output the atlases to
    :return: None
    """
    os.mkdir(output_directory)
    for file in get_files_of_type(pbf_directory, PBF_EXTENSION):
        LOGGER.info("Generating Atlas for {}".format(file))
        sub_run_string("java -Xms2048m -Xmx10240m -cp {} org.openstreetmap.atlas.geography.atlas.command.AtlasReader "
                       "pbf-to-atlas -pbf={} -output={}.atlas -country-boundary-map={} -country-codes={}"
                       .format(atlas_jar, file, output_directory+os.path.split(file)[1][:-8], country_boundary_map,
                               iso_codes))


def safe_rm_dir(dir_path):
    """
    Remove a directory recursively, if it exists.

    :param dir_path: path of the directory to remove.
    :return: None
    """
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


def clean_outputs():
    """
    Remove all the output directories.

    :return: None
    """
    if os.path.isfile(EXTRACT_CONFIG_FILE_PATH):
        os.remove(EXTRACT_CONFIG_FILE_PATH)
    safe_rm_dir(EXTRACT_PBFS_DIRECTORY_PATH)
    safe_rm_dir(TEMP_DIRECTORY_PATH)
    safe_rm_dir(TIME_SLICES_ONE_DIRECTORY)
    safe_rm_dir(TIME_SLICES_TWO_DIRECTORY)
    safe_rm_dir(TIME_SLICES_ONE_CLEAN_DIRECTORY)
    safe_rm_dir(TIME_SLICES_TWO_CLEAN_DIRECTORY)


def main():
    """
    Run the program.

    :return: None
    """
    s_time = time.time()

    LOGGER.info("Getting arguments")
    args = get_args()

    LOGGER.info("Cleaning outputs")
    clean_outputs()

    LOGGER.info("Generating extract config file")
    generate_extracts_config(get_files_of_type(args.geojsons_folder_path, ".geojson"))

    LOGGER.info("Extracting by location")
    extract_history_files(args.pbf_path)

    LOGGER.info("Creating time slices for {}".format(args.timestamp1))
    time_slice_pbfs(args.timestamp1, TIME_SLICES_ONE_DIRECTORY)
    LOGGER.info("Creating time slices for {}".format(args.timestamp2))
    time_slice_pbfs(args.timestamp2, "time_slices2/")

    LOGGER.info("Cleaning {} pbfs".format(args.timestamp1))
    clean_pbfs(TIME_SLICES_ONE_DIRECTORY, TIME_SLICES_ONE_CLEAN_DIRECTORY)
    LOGGER.info("Cleaning {} pbfs".format(args.timestamp2))
    clean_pbfs(TIME_SLICES_TWO_DIRECTORY, TIME_SLICES_TWO_CLEAN_DIRECTORY)

    LOGGER.info("Generating {} atlases".format(args.timestamp1))
    generate_atlases(TIME_SLICES_ONE_CLEAN_DIRECTORY, args.atlas_jar, args.country_boundary_map, args.iso_codes,
                     "atlases_{}/".format(args.timestamp1.replace(":", "-")))
    LOGGER.info("Generating {} atlases".format(args.timestamp2))
    generate_atlases(TIME_SLICES_TWO_CLEAN_DIRECTORY, args.atlas_jar, args.country_boundary_map, args.iso_codes,
                     "atlases_{}/".format(args.timestamp2.replace(":", "-")))

    LOGGER.info("Done in {} minutes".format((time.time()-s_time)/60))


if __name__ == "__main__":
    main()