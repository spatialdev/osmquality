import json
import numpy as np
import os
import csv
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class Utility:
    """ Uitlity class.

    This class consists of several file-writer and data-generator functions and a distribution-computation function.
    
    """
    
    def __init__(self):
        """ The docstring of the __init__ method.

        write out a blank line to standard error
        
        """
        sys.stderr.write('\n')

    def __del__(self):
        """ The doctring of the __del__ method.

        write out a message of deleting Utility module to standard error
        
        """
        sys.stderr.write("deling" + str(self) + '\n')
    
    def distribution_computation(self, name, input_histogram):
        """ Distribution computation method.

        This method calculates the probability distribution from object counts, and creaete a histogram and save it.

        Args:
            name: a file path to an output histogram plot.
            input_histogram: a count list to geometries over all grids.
            
        Returns:
            statistics_result: a dictionary in which key and value represent the number of flagged features and counts, respectively.
            x_axis: a list to the number of flagged features.
            count_0_pair: a pair to the number of grids with zero flagged feature.
            len(statistics_result): the number of keys in the dictionary.
            
        Examples:
            x-axis of the plot: (1) Counts (or other measurements) or (2) Number of Flagged Features.
            y-axis of the plot: (1) # of cells that has that counts/value (Frequency) or (2) Number of Grids.
        
        """
        # create X-axis and a histogram for a given input count array
        count_0_pair = []
        statistics_result = dict((i, list(input_histogram).count(i)) for i in list(input_histogram))
        statistics_result = dict(sorted(statistics_result.items()))
        if 0 in statistics_result:
            count_0_pair = [0, statistics_result[0]]
        statistics_result.pop(0, None)
        x_axis = list(statistics_result.keys())


        # plot histograms
        fig, ax = plt.subplots()
        ax.bar(range(len(statistics_result)), list(statistics_result.values()), align='center')
        plt.xticks((0, len(statistics_result) - 1), (x_axis[0], x_axis[len(statistics_result) - 1]))
        plt.xlabel('Number of Flagged Features')
        plt.ylabel('Number of Grids')
        fig.savefig(name)

        
        return statistics_result, x_axis, count_0_pair, len(statistics_result)
    
    def geojson_write(self, level_val, bounding_box_collec, directory_path, cell_num, input_grid_area, in_grid_ids, kd_tree_mode, input_counts, flag_val):
        """ A geojson writer.

        This method writes out a GeoJson file.
        
        Args:
            level_val: tree depth.
            bounding_box_collec: a bounding-box list.
            directory_path: a directory path.
            cell_num: the number of grids with unrepeated flagged features.
            input_grid_area: a grid area.
            in_grid_ids: a grid-id list.
            kd_tree_mode: a value to choose different modes (tree_v1 or cascade-kdtree).
            input_counts: a count list to geometries over all grids.
            flag_val: a flag to create a new grid-id list or not.
            
        Examples:
            ploygon format:
                [ [
                    [-180.0, 79.1713346],
                    [-180.0, 85.0511288],
                    [-135.0, 85.0511288],
                    [-135.0, 79.1713346]
                  ]
                ]
        
        """
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
        
    def csv_writer(self, write_out_data, output_path):
        """ a CSV writer.

        This method writes out a csv file.

        Args:
            write_out_data: a two-dimensional matrix that is prepared to write out.
            output_path: a file path to a csv file.
        
        """
        # write out the data as a csv file
        with open(output_path, "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerows(write_out_data)
    
    def summary_table_row_generation(self, input_data, name_number_file, initial_extend, gridsize, folder_name):
        """ A row generation to a summary table.

        This method generates a row of a summary table.

        Args:
            input_data: a two-dimensional list with some important information.
            name_number_file: a two-dimensional list with check names and the number of counts.
            initial_extend: size of an initial extend.
            gridsize: grid size.
            folder_name: a folder name.
            
        Returns:
            [folder_name, flags, len(osm_features), initial_extend, gridsize]: an output list with a folder name, # of flags, # of osm features, the size of an initial extend, and grid size.
        
        """
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
        return [folder_name, flags, len(osm_features), initial_extend, gridsize]
    
    def get_sub_directionaries(self, folder_path):
        """ Sub-directionary grabbing.

        This method is to get all of the sub-directionaries.
        
        Args:
            folder_path: a folder path.
            
        """
        return [os.path.join(os.path.join(folder_path, sub_folder)) for sub_folder in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, sub_folder))]
