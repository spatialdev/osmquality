import json
import numpy as np
import sys, os, csv
from kd_tree import kdTree
from utility import Utility
import argparse
import ast

# Road counts
def road_count(in_road, in_grids, in_counts, out_folder, initial_bb):
    road_data = []
    road_counts_his = np.zeros(len(in_grids))
    # load the Geo-json file and ignore other files
    if os.path.splitext(in_road)[1] == '.geojson':
        # open geojson files
        with open(in_road, encoding='utf-8') as new_f:
            in_data = json.load(new_f)
        
        # process all geometries excluding the 1st one
        for index in range(len(in_data['features'])):
            # discard a feature without its feature property
            if len(in_data['features'][index]['properties']) != 0:
                road_data.append([in_data['features'][index]['geometry']['type'], in_data['features'][index]['geometry']['coordinates']])

        # calculate the number of counts within a grid giving the road data
        for index2 in range(len(road_data)):
            if road_data[index2][0] == 'LineString':
                np_array = np.array(road_data[index2][1])
                tmp_array = np.zeros(len(in_grids))

                # iterate through all grids
                for ind in range(len(in_grids)):
                    for coordinate_ind in range(np_array.shape[0]):
                        if in_grids[ind][3] == initial_bb[3] and in_grids[ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] <= in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] <= in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] == initial_bb[3] and in_grids[ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] < in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] <= in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] != initial_bb[3] and in_grids[ind][2] == initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] <= in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] < in_grids[ind][3]):
                                tmp_array[ind] += 1
                        elif in_grids[ind][3] != initial_bb[3] and in_grids[ind][2] != initial_bb[2]:
                            if (np_array[coordinate_ind, :][0] >= in_grids[ind][0] and np_array[coordinate_ind, :][0] < in_grids[ind][2] and
                                np_array[coordinate_ind, :][1] >= in_grids[ind][1] and np_array[coordinate_ind, :][1] < in_grids[ind][3]):
                                tmp_array[ind] += 1                
        
                for ind2 in range(len(in_grids)):
                    if tmp_array[ind2] > 0:
                        road_counts_his[ind2] += 1
        # ==========================================
        # write out a csv file
        csv_matrix = []
        csv_matrix.append(['grid_id', 'err_roads', 'road_counts'])
        for index in range(len(in_grids)):
            csv_matrix.append([index + 1, in_counts[index], road_counts_his[index]])
            
        with open(os.path.join(out_folder, 'road-' + os.path.basename(out_folder) + '.csv'), "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerows(csv_matrix)
# =======================================
def main():
    # declare arguments and variables
    parser = argparse.ArgumentParser()
    parser.add_argument('--maxDepth', type = str, default='', help='max depth of a k-d tree')
    parser.add_argument('--countNum', type = str, default='', help='a count value')
    parser.add_argument('--gridPercent', type = str, default='', help='a grid percentage')
    parser.add_argument('--maxCount', type = str, default='', help='maximum count to the second k-d tree')
    parser.add_argument('--outFolder', type = str, default='', help='path to an ouput folder')

    args = parser.parse_args()
    maximum_level = args.maxDepth
    folder_path = args.outFolder
    count_num = int(args.countNum)
    grid_percent = float(args.gridPercent)
    
    path = 'histogram'
    geojson_path = 'geojson'
    
    if not os.path.exists(os.path.join(folder_path, path)):
        sys.stderr.write('Create the histogram directory !! \n')
        os.makedirs(os.path.join(folder_path, path))
    if not os.path.exists(os.path.join(folder_path, geojson_path)):
        sys.stderr.write('Create the geojson directory !! \n')
        os.makedirs(os.path.join(folder_path, geojson_path))
    
    max_count = 0
    flag_val = False
    input_data = None
    optimal_count_list = None
    optimal_grid_size_list = None
    first_depth = 0
    big_initial_area = 0.0

    if args.maxCount:
        max_count = int(args.maxCount)

    # read L-2 dissimilarity from stand input
    for line in sys.stdin.readlines():
        input_data = ast.literal_eval(line)
    
    # save the 2d list as a file
    with open(os.path.join(folder_path, os.path.basename(input_data['inFolder']) + '.csv' )  , "w") as out_f:
        writer = csv.writer(out_f)
        writer.writerows(input_data['nameNum'])
    
    # perform the 1st k-d tree
    for depth_count in range(1, int(maximum_level) + 1):
        # build k-d tree
        tree_cons = kdTree(depth_count, input_data['iniBb'], input_data['data'], 1)
        out_tree = tree_cons.tree_building()

        # get leaves given a K-D tree
        bb_collec = tree_cons.get_leaves(out_tree)

        # get counts
        hist, gridid_collec= tree_cons.counts_calculation()
        del tree_cons

        util = Utility(hist)
        filename = os.path.join(os.path.join(folder_path, path), 'level-' + str(depth_count) + '.png')
        # probability distribution
        out_distribution, count_list, count_zero_list, cell_num = util.distribution_computation(filename)
        # write out a Geojson file
        util.geojson_write(depth_count, bb_collec, os.path.join(folder_path, geojson_path), cell_num, input_data['iniArea'], None, 'tree_v1', flag_val)
        del util

        # stop condition (the over 90% (parameter) of cells is less than 10 (parameter) (the count value))
        if len(count_zero_list) != 0:
            count_list.insert(0, count_zero_list[0])
        smallest_max_count = 0
        smallest_max_count_ind = -1
        for ind, ele in enumerate(count_list):
            if ele > count_num:
                break
            else:
                smallest_max_count = ele
                smallest_max_count_ind = ind

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

            if (float(total_count_within_count_num) / float(total_grids)) > grid_percent:
                util = Utility(hist)
                # calculate areas
                grid_area = input_data['iniArea'] / (2**(depth_count))
                grid_area = round(grid_area * 1e-6, 2)

                # wirte out one row
                util.summary_table_row_generation(input_data['data'], input_data['nameNum'], round(input_data['iniArea'] * 1e-6, 2), grid_area)
                
                # write out a Geojson file
                util.geojson_write(depth_count, bb_collec, os.path.join(folder_path, geojson_path), cell_num, input_data['iniArea'],
                                   None, 'tree_v1', flag_val = True)
                if args.maxCount:
                    optimal_grid_size_list = bb_collec
                    optimal_count_list = hist
                    first_depth = depth_count
                    big_initial_area = grid_area
                    
                # road counts
                if input_data['roadFile']:
                    road_count(input_data['roadFile'], bb_collec, hist, folder_path, input_data['iniBb'])
                del util
                break
    # ======================================
    # perform the 2nd k-d tree
    if args.maxCount:
        big_grid_list = []
        new_grids_list = []
        new_counts_list = []
        new_area_list = []
        new_grid_id_list = []
        grid_ids = []
        gridid_start = 1
        # find all grids in which the count is greater the max count
        for index in range(len(optimal_grid_size_list)):
            if optimal_count_list[index] > max_count:
                big_grid_list.append(optimal_grid_size_list[index])
        if len(big_grid_list) != 0:
            # refine big grids through applying the 2nd K-D tree
            for extension_ind in range(len(big_grid_list)):
                for depth_num in range(1, int(maximum_level) + 1):
                    # build k-d tree
                    new_tree_cons = kdTree(depth_num, big_grid_list[extension_ind], input_data['data'], gridid_start)
                    new_kd_tree = new_tree_cons.tree_building()
                    new_bb_collec = new_tree_cons.get_leaves(new_kd_tree)
                    # get counts
                    new_counts_collec, new_grid_id_collec = new_tree_cons.counts_calculation()
                    new_grid_id_list.append(new_grid_id_collec)
                    # calculate areas
                    new_area = big_initial_area / (2** depth_num)
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
            # ======================================
            util = Utility(new_counts_list)
            
            # write out a Geojson file
            util.geojson_write(first_depth, new_grids_list,
                               os.path.join(folder_path, geojson_path), None, None, grid_ids, 'cascade-kdtree', flag_val = True)
            sys.stderr.write("Grid number after the 2nd k-d tree: " + str(len(new_grids_list)) + '\n')
            sys.stderr.write("Count number after the 2nd k-d tree::" + str(len(new_counts_list)) + '\n')
            del util
if __name__ == "__main__":
    main()
