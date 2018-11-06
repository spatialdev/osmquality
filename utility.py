import json
import numpy as np
import os, csv, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Utility:
    def __init__(self):
        sys.stderr.write('\n')
    def __del__(self):
        sys.stderr.write("deling" + str(self) + '\n')
    # =====================================
    # calculate the probability distribution from object counts, and creaete a histogram and save it
    def distribution_computation(self, name, input_histogram):
        # create X-axis and Y-axis in order to plot histograms
        """
        X - Counts (or other measurements)
        Y - # of cells that has that counts/value (Frequency)
        """
        statistics_result = dict((i, list(input_histogram).count(i)) for i in list(input_histogram))
        statistics_result = dict(sorted(statistics_result.items()))
        
        count_0_pair = []
        if 0 in statistics_result:
            count_0_pair = [0, statistics_result[0]]
        
        statistics_result.pop(0, None)
        
        x_axis = list(statistics_result.keys())
        
        fig, ax = plt.subplots()
        ax.bar(range(len(statistics_result)), list(statistics_result.values()), align='center')
        plt.xticks((0, len(statistics_result) - 1), (x_axis[0], x_axis[len(statistics_result) - 1]))
        plt.xlabel('Number of Flagged Features')
        plt.ylabel('Number of Grids')
        fig.savefig(name)
        
        return statistics_result, x_axis, count_0_pair, len(statistics_result)
    # =====================================
    # Write out geojson file
    # Polygon Format:
    # [ [
    #      [-180.0, 79.1713346],
    #      [-180.0, 85.0511288],
    #      [-135.0, 85.0511288],
    #      [-135.0, 79.1713346]
    #   ]
    # ]
    def geojson_write(self, level_val, bounding_box_collec, directory_path, cell_num, input_grid_area, in_grid_ids, kd_tree_mode, input_counts, flag_val):
        # declare variables
        file_path = ''
        json_dic = {}
        feature_list = []
        json_dic['type'] = 'FeatureCollection'

        # add all cells and counts into the feature list
        for index in range(len(input_counts)):
            tmp_dic = {}
            geometry_dic = {}
            properties_dic = {}
            geometry_dic['type'] = 'Polygon'
            geometry_dic['coordinates'] = [[ [bounding_box_collec[index][0],bounding_box_collec[index][1]],
                                         [bounding_box_collec[index][0],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][1]] ]]
        
            properties_dic['counts'] = input_counts[index]
            if flag_val:
                if in_grid_ids is None:
                    properties_dic['gridId'] = index + 1
                else:
                    properties_dic['gridId'] = in_grid_ids[index]

            tmp_dic['type'] = 'Feature'
            tmp_dic['geometry'] = geometry_dic
            tmp_dic['properties'] = properties_dic
            feature_list.append(tmp_dic)
            del tmp_dic
            del geometry_dic
            del properties_dic
        json_dic['features'] = feature_list

        # save the dictionary structure as a Geojson file
        if kd_tree_mode == 'tree_v1':
            file_path = os.path.join(directory_path, 'level-' + str(level_val) + '-' + str(cell_num) + '_area_' + str(input_grid_area) + '_sq_kms' + '.geojson')
        elif kd_tree_mode == 'cascade-kdtree':
            file_path = os.path.join(directory_path, 'first-depth-' + str(level_val) + '.geojson')

        with open(file_path, 'w') as f:
            json.dump(json_dic, f)
    # =====================================
    def csv_writer(self, write_out_data, output_path):
        # write out the data as a csv file
        with open(output_path, "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerows(write_out_data)
    # =====================================
    # generate a row of a summary table
    def summary_table_row_generation(self, input_data, name_number_file, initial_extend, gridsize, folder_name):
        # variables
        flags = 0
        osm_features = {}
        
        # calculate total flags
        for element_index in range(1, len(name_number_file)):
            flags += int(name_number_file[element_index][1])
        # calculate the unique number of OSM features
        for row in input_data:
            osm_features[int(row[3])] = osm_features.get(int(row[3]), 0) + 1
        # return one row
        return [folder_name,flags, len(osm_features), initial_extend, gridsize]
    # =====================================
    def get_sub_directionaries(self, folder_path):
        return [os.path.join(os.path.join(folder_path, sub_folder)) for sub_folder in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, sub_folder))]
