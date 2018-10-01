import json
import numpy as np
import os, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Utility:
    def __init__(self, input_histogram):
        self.hist = input_histogram
    def __del__(self):
        print("deling", self)
    # =====================================
    # calculate the probability distribution given a histogram
    def distribution_computation(self, name):
        # create X-axis and Y-axis in order to plot histograms
        """
        X - Counts (or other measurements)
        Y - # of cells that has that counts/value (Frequency)
        """
        statistics_result = dict((i, list(self.hist).count(i)) for i in list(self.hist))
        statistics_result = dict(sorted(statistics_result.items()))
        count_0_pair = []
        if 0 in statistics_result:
            count_0_pair = [0, statistics_result[0]]
        
        statistics_result.pop(0, None)

        x_axis = list(statistics_result.keys())

        fig, ax = plt.subplots()
        ax.bar(range(len(statistics_result)), list(statistics_result.values()), align='center')
        plt.xticks((0, len(statistics_result) - 1), (x_axis[0], x_axis[len(statistics_result) - 1]))
        plt.xlabel('Counts (or other measurements)')
        plt.ylabel('Frequency (# of grids has that counts)')
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
    def geojson_write(self, level_val, bounding_box_collec, directory_path, cell_num, initial_area, in_grid_ids, kd_tree_mode, flag_val):
        # declare variables
        json_dic = {}
        feature_list = []
        json_dic['type'] = 'FeatureCollection'

        # add all cells and counts into the feature list
        for index in range(len(self.hist)):
            tmp_dic = {}
            geometry_dic = {}
            properties_dic = {}
            geometry_dic['type'] = 'Polygon'
            geometry_dic['coordinates'] = [[ [bounding_box_collec[index][0],bounding_box_collec[index][1]],
                                         [bounding_box_collec[index][0],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][3]],
                                         [bounding_box_collec[index][2],bounding_box_collec[index][1]] ]]
        
            properties_dic['counts'] = self.hist[index]
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
            #grid_area = initial_area / (2**(level_val + 1))
            grid_area = initial_area / (2**(level_val))
            grid_area = round(grid_area * 1e-6, 2)

            with open(os.path.join(directory_path, 'level-' + str(level_val) + '-' + str(cell_num) + '_area_' + str(grid_area) + '_sq_kms' + '.geojson'), 'w') as f:
                json.dump(json_dic, f)
        elif kd_tree_mode == 'tree_v2':
            with open(os.path.join(directory_path, 'max-depth-' + str(level_val) + '-' + 'cell_num' + str(cell_num) + '.geojson'), 'w') as f:
                json.dump(json_dic, f)
        elif kd_tree_mode == 'cascade-kdtree':
            with open(os.path.join(directory_path, 'first-depth-' + str(level_val) + '.geojson'), 'w') as f:
                json.dump(json_dic, f)
    # =====================================
    # Create a table and save it as a csv file
    def csv_file_write(self, in_data, in_grid_collec_list, in_path, area_list):
        out_list = []
        out_list.append(['grid_id', 'atlas_id', 'osm_id', 'flag_id', 'check_name', 'area_sqkm'])
        if len(in_grid_collec_list) == 1:
            for index in range(len(in_data)):
                if in_data[index][0] == 'Point' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[0]:
                    out_list.append([in_grid_collec_list[0][    in_data[index][4] + '-' + in_data[index][0] ], in_data[index][4],
                                  in_data[index][3], in_data[index][2], in_data[index][5], area_list[0]
                                  ])
                elif in_data[index][0] == 'LineString' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[0]:
                    for elem_id in in_grid_collec_list[0][in_data[index][4] + '-' + in_data[index][0] ]:
                        out_list.append([elem_id, in_data[index][4], in_data[index][3], in_data[index][2], in_data[index][5], area_list[0]])
        else:
            for index in range(len(in_data)):
                # iterate through all grid-id dictionaries
                for dic_index in range(len(in_grid_collec_list)):
                    if in_data[index][0] == 'Point' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[dic_index]:
                        out_list.append([in_grid_collec_list[dic_index][in_data[index][4] + '-' + in_data[index][0] ], in_data[index][4],
                                     in_data[index][3], in_data[index][2], in_data[index][5], area_list[dic_index]
                                     ])
                    elif in_data[index][0] == 'LineString' and in_data[index][4] + '-' + in_data[index][0] in in_grid_collec_list[dic_index]:
                        for elem_id in in_grid_collec_list[dic_index][in_data[index][4] + '-' + in_data[index][0] ]:
                            out_list.append([elem_id, in_data[index][4], in_data[index][3], in_data[index][2], in_data[index][5], area_list[dic_index]])
        # save the 2d list as a file
        with open(in_path, "w") as out_f:
            writer = csv.writer(out_f)
            writer.writerows(out_list)
    # =====================================










