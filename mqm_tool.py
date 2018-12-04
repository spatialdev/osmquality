import json
import numpy as np
import sys
import os
import csv
from kd_tree import kdTree
from utility import Utility
from geoProcess import GeoProcessor
import argparse
import ast


def road_count(in_road, in_grids, in_counts, out_folder, initial_bb):
    """ Road count function.

    This function calculates the number of flagged features in all of the grids for a given road file.
    
    Args:
        in_road: a road file.
        in_grids: a collection of bounding boxes.
        in_counts: a count list in which every entry stores the number of flagged features to each grid.
        out_folder: a folder path.
        initial_bb: an initial bounding box.
        
    """
    road_data = []
    road_counts_his = np.zeros(len(in_grids))
    csv_matrix = []
    csv_matrix.append(['grid_id', 'err_roads', 'road_counts'])

    
    # load the Geo-json file and ignore other files
    if os.path.splitext(in_road)[1] == '.geojson':
        # open geojson files
        with open(in_road, encoding='utf-8') as new_f:
            in_data = json.load(new_f)
        
        # extract all geometries from the geojson file
        for geometry_index in range(len(in_data['features'])):
            # discard a feature without its feature property
            if len(in_data['features'][geometry_index]['properties']) != 0:
                road_data.append([in_data['features'][geometry_index]['geometry']['type'],
                                  in_data['features'][geometry_index]['geometry']['coordinates']])

        # calculate the number of counts within a grid giving the road data
        for data_index in range(len(road_data)):
            if road_data[data_index][0] == 'LineString':
                np_array = np.array(road_data[data_index][1])
                tmp_array = np.zeros(len(in_grids))

                # iterate through all grids
                for grid_array_ind in range(len(in_grids)):
                    for coordinate_ind in range(np_array.shape[0]):
                        if in_grids[grid_array_ind][3] == initial_bb[3] and in_grids[grid_array_ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[grid_array_ind][0] and
                                np_array[coordinate_ind, :][0] <= in_grids[grid_array_ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[grid_array_ind][1] and
                                np_array[coordinate_ind, :][1] <= in_grids[grid_array_ind][3]):
                                tmp_array[grid_array_ind] += 1
                                
                        elif in_grids[grid_array_ind][3] == initial_bb[3] and in_grids[grid_array_ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[grid_array_ind][0] and
                                np_array[coordinate_ind, :][0] < in_grids[grid_array_ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[grid_array_ind][1] and
                                np_array[coordinate_ind, :][1] <= in_grids[grid_array_ind][3]):
                                tmp_array[grid_array_ind] += 1
                                
                        elif in_grids[grid_array_ind][3] != initial_bb[3] and in_grids[grid_array_ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[grid_array_ind][0] and
                                np_array[coordinate_ind, :][0] <= in_grids[grid_array_ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[grid_array_ind][1] and
                                np_array[coordinate_ind, :][1] < in_grids[grid_array_ind][3]):
                                tmp_array[grid_array_ind] += 1
                                
                        elif in_grids[grid_array_ind][3] != initial_bb[3] and in_grids[grid_array_ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[grid_array_ind][0] and
                                np_array[coordinate_ind, :][0] < in_grids[grid_array_ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[grid_array_ind][1] and
                                np_array[coordinate_ind, :][1] < in_grids[grid_array_ind][3]):
                                tmp_array[grid_array_ind] += 1                
        
                for grid_array_ind in range(len(in_grids)):
                    if tmp_array[grid_array_ind] > 0:
                        road_counts_his[grid_array_ind] += 1
        # ==========================================
        for array_index in range(len(in_grids)):
            csv_matrix.append([array_index + 1, in_counts[array_index], road_counts_his[array_index]])

        # write out a csv file
        util = Utility()
        util.csv_writer(csv_matrix, os.path.join(out_folder, 'road-' + os.path.basename(out_folder) + '.csv'))
        

def get_argument():
    """ Argument grabbing function.

    This function grabs all of the arguments that the program needs.
    
    Returns:
        args.folderPath: an input folder path.
        args.maxDepth: a maximum tree depth.
        output_folder: a result folder.
        int(args.countNum): a count number for a stop condition in the first k-d tree.
        float(args.gridPercent): a percetage value for grids.
        max_count: a maximum count in the second k-d tree.
        path: a path to a histogram folder.
        geojson_path: a path to a geojson folder.
        
    """
    # declare arguments and variables
    parser = argparse.ArgumentParser()
    parser.add_argument('--folderPath', type = str, default='', help='path to an input folder')
    parser.add_argument('--maxDepth', type = str, default='10', help='max depth of a k-d tree')
    parser.add_argument('--countNum', type = str, default='10', help='a count value for a stop condition')
    parser.add_argument('--gridPercent', type = str, default='0.9', help='a grid percentage')
    parser.add_argument('--maxCount', type = str, default='', help='maximum count to the second k-d tree')
    args = parser.parse_args()
    max_count = -1
    path = 'histogram'
    geojson_path = 'geojson'
    output_folder = os.path.join(os.path.split(args.folderPath)[0], 'result')

    
    if args.maxCount:
        max_count = int(args.maxCount)

    
    return args.folderPath, args.maxDepth, output_folder, int(args.countNum), float(args.gridPercent), max_count, path, geojson_path


def stop_condition(count_zero_list, count_list, grid_percent, count_num, cell_num, out_distribution):
    """ Stop condition function.

    This function calculates the stop condition to the first k-d tree.

    Args:
        count_zero_list: a pair to the number of grids with zero flagged feature.
        count_list: a list to the number of flagged features.
        grid_percent: a percetage value for grids.
        count_num: a count number for a stop condition in the first k-d tree.
        cell_num: the number of keys in the dictionary.
        out_distribution: a dictionary in which key and value represent the number of flagged features and counts, respectively.
        
    Returns:
        stop_flag: a flag value that indicates
        
    """
    # varialbes
    smallest_max_count = 0
    smallest_max_count_ind = -1
    stop_flag = False

    
    # add zeon-count back to the count list and find a maximum count that is smaller than a threshold
    if count_zero_list:
        count_list.insert(0, count_zero_list[0])
    for ind, ele in enumerate(count_list):
        if ele > count_num:
            break
        
        else:
            smallest_max_count = ele
            smallest_max_count_ind = ind

    
    # check the stop condition
    if smallest_max_count_ind != -1:
        total_count_within_count_num = 0
        total_grids = 0
        list_length = 0

        if not count_zero_list:  # the list is empty
            list_length = smallest_max_count_ind + 1
            total_grids = cell_num
            
        else:
            list_length = smallest_max_count_ind + 2
            total_grids = cell_num + count_zero_list[1]

        for i in range(list_length):
            if count_list[i] == 0:
                total_count_within_count_num += count_zero_list[1]
                
            else:
                total_count_within_count_num += out_distribution[count_list[i]]
        
        if (float(total_count_within_count_num / total_grids)) > grid_percent:
            stop_flag = True
    
    
    return stop_flag


def extend_partition(depth_count, input_bounding_box, input_data, startId):
    """ Extend partition function.

    This function is to partition an initial extend to multiple grids.

    Args:
        depth_count: tree depth.
        input_bounding_box: a bounding box.
        input_data: a nested list that consists of important information.
        startId: a start id.
        
    Returns:
        bounding_box_collection: a collection of bounding boxes.
        count_list: a count list in which every entry stores the number of flagged features to each grid.
        gridid_collec: a collection of grid ids.
        
    """
    # build k-d tree
    tree_cons = kdTree(depth_count, input_bounding_box, input_data, startId)
    kd_tree= tree_cons.tree_building()

    
    # get all the leaves given a K-D tree
    bounding_box_collection = tree_cons.get_leaves(kd_tree)

    
    # get counts
    count_list, gridid_collec= tree_cons.counts_calculation()

    
    return bounding_box_collection, count_list, gridid_collec


def directory_creation(result_folder_path, sub_folder, path, geojson_path):
    """ Directory creation function.

    This function is to make all of the directories that the program needs.

    Args:
        result_folder_path: a result folder.
        sub_folder: a sub-folder inside the result folder.
        path: a path to a histogram folder.
        geojson_path: a path to a geojson folder.
        
    """
    if not os.path.exists(result_folder_path):
        sys.stderr.write('Create a result directory !! \n')
        os.makedirs(result_folder_path)
        
    if not os.path.exists(os.path.join(sub_folder, path)):
        sys.stderr.write('Create a histogram directory !! \n')
        os.makedirs(os.path.join(sub_folder, path))
        
    if not os.path.exists(os.path.join(sub_folder, geojson_path)):
        sys.stderr.write('Create a geojson directory !! \n')
        os.makedirs(os.path.join(sub_folder, geojson_path))
        

def process_single_folder(input_folder, folder_path, maximum_level, count_num, grid_percent, max_count, path, geojson_path, flag_val, summary_table, folder_name):
    """ Single folder process.

    This function processes a single folder and runs a k-d tree algorithm.

    Args:
        input_folder: a folder name. 
        folder_path: a folder path.
        maximum_level: a maximum tree depth.
        count_num: a count number for a stop condition in the first k-d tree.
        grid_percent: a percetage value for grids.
        max_count: a maximum count in the second k-d tree.
        path: a path to a histogram folder.
        geojson_path: a path to a geojson folder.
        flag_val: a flag value.
        summary_table: a summary table including check names and feature counts.
        folder_name: a last folder name for a given folder path.
        
    """
    # read and parse all geoJson files
    geo_processor = GeoProcessor(input_folder)
    entire_data, out_BB, name_num = geo_processor.bounding_box_process()
    road_file = geo_processor.get_road_file()
    initial_area = geo_processor.get_initial_extend_area(out_BB)
    del geo_processor

    
    util = Utility()
    util.csv_writer(name_num, os.path.join(folder_path, os.path.basename(input_folder) + '.csv' ))
    del util

    
    # perform the 1st k-d tree
    for depth_count in range(1, int(maximum_level) + 1):
        bb_collec, hist, _ = extend_partition(depth_count, out_BB, entire_data, 1)

        # calculate areas
        grid_area = initial_area / (2**(depth_count))
        grid_area = round(grid_area * 1e-6, 2)
        
        util = Utility()
        filename = os.path.join(os.path.join(folder_path, path), 'level-' + str(depth_count) + '.png')
        # probability distribution
        out_distribution, count_list, count_zero_list, cell_num = util.distribution_computation(filename, hist)
        # write out a Geojson file
        util.geojson_write(depth_count, bb_collec, os.path.join(folder_path, geojson_path), cell_num, grid_area, None, 'tree_v1', hist, flag_val)

        # stop condition (the over 90% (parameter) of cells is less than 10 (parameter) (the count value))
        if stop_condition(count_zero_list, count_list, grid_percent, count_num, cell_num, out_distribution):
            # wirte out one row
            summary_table.append(util.summary_table_row_generation(entire_data, name_num, round(initial_area * 1e-6, 2), grid_area, folder_name))

            # write out a Geojson file
            util.geojson_write(depth_count, bb_collec, os.path.join(folder_path, geojson_path), cell_num, grid_area,
                               None, 'tree_v1', hist, flag_val = True)
            del util
            
            # perform the 2nd k-d tree
            if max_count != -1:                
                new_grids_list = []
                new_counts_list = []
                new_area_list = []
                new_grid_id_list = []
                grid_ids = []
                gridid_start = 1
                
                # find all grid indices in which the count is greater the max count
                big_grid_index_list = [index_value for index_value in range(hist.shape[0]) if hist[index_value] > max_count]
                if big_grid_index_list:
                    # refine big grids through applying the 2nd K-D tree
                    for extension_ind in big_grid_index_list:
                        for depth_num in range(1, int(maximum_level) + 1):
                            new_bb_collec, new_counts_collec, new_grid_id_collec = extend_partition(depth_num, bb_collec[extension_ind], entire_data, gridid_start)
                            new_grid_id_list.append(new_grid_id_collec)

                            # calculate areas
                            new_area = grid_area / (2** depth_num)
                            new_area_list.append(new_area)

                            # update the start point of the grid id
                            gridid_start += len(new_bb_collec)

                            # stop condition
                            if len([x for x in new_counts_collec if x < max_count]) == len(new_counts_collec):
                                for small_ind in range(len(new_bb_collec)):
                                    grid_ids.append(gridid_start + small_ind - len(new_bb_collec))
                                    new_grids_list.append(new_bb_collec[small_ind])
                                    new_counts_list.append(new_counts_collec[small_ind])
                                break
                    
                    util = Utility()
                    # write out a Geojson file
                    util.geojson_write(depth_count, new_grids_list,
                                       os.path.join(folder_path, geojson_path), None, None, grid_ids, 'cascade-kdtree', new_counts_collec, flag_val = True)
                    del util
            
            # road counts
            if road_file:
                road_count(road_file, bb_collec, hist, folder_path, out_BB)
            break


def main():
    """ A main function.

    This function is to parse all of the Geo-json files and perform all of the functions.
    
    """
    # get all arguments
    input_folder, maximum_level, folder_path, count_num, grid_percent, max_count, path, geojson_path = get_argument()
    flag_val = False
    summary_table = []
    summary_table.append(['name','flags','flagged_OSM_feature','totalArea','gridSize'])

    
    # get a sub-directory list
    util = Utility()
    folder_list = util.get_sub_directionaries(input_folder)
    del util

    
    # iterate through all sub-directories
    for sub_folder in folder_list:
        directory_creation(folder_path, os.path.join(folder_path, os.path.split(sub_folder)[1]), path, geojson_path)
        
        # process single sub-folder
        process_single_folder(sub_folder, os.path.join(folder_path, os.path.split(sub_folder)[1]), maximum_level,
                              count_num, grid_percent, max_count, path, geojson_path, flag_val, summary_table,
                              os.path.split(sub_folder)[1])

    
    # write out a summary table
    util = Utility()
    util.csv_writer(summary_table, os.path.join(folder_path, 'road-summary.csv'))

    
if __name__ == "__main__":
    """ A function to call the main function.
    """
    main()
