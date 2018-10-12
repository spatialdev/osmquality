import json
import numpy as np
import sys, os
from area import area
import argparse

def final_bounding_box_generation(input_list, column_length):
    x_min = x_max = y_min = y_max = 0
    if column_length == 4:
        np_geometry_bounding_box_list = np.asarray(input_list)
        _, _, x_max, y_max = np_geometry_bounding_box_list.max(axis = 0)
        x_min, y_min, _, _ = np_geometry_bounding_box_list.min(axis = 0)
    elif column_length == 2:
        x_max, y_max = input_list.max(axis = 0)
        x_min, y_min = input_list.min(axis = 0)
    return [x_min, y_min, x_max, y_max]

# =======================================
def high_dimension_computation(in_matrix):
    storage_list = []
    for list_index in range(len(in_matrix)):
        storage_list.append(final_bounding_box_generation(np.array(in_matrix[list_index]), 2))
    return final_bounding_box_generation(storage_list, 4)

# =======================================
def min_max_calculation(geo_type, in_coordinates):
    # declare variable
    the_bounding_box = None
    
    # find the minimum and maximum value based on geometry types
    if geo_type == 'Point' or geo_type == 'LineString' or geo_type == 'MultiPoint':
        np_array = np.array(in_coordinates)
        dim_value = len(np_array.shape)
        if dim_value == 1:
            # find the minimum and maximum value directly
            the_bounding_box = [np_array[0], np_array[1], np_array[0], np_array[1]]
        elif dim_value == 2:
            # find the minimum and maximum values through comparing all elements in individual columns
            the_bounding_box = final_bounding_box_generation(np_array, 2)
            
    elif geo_type == 'Polygon' or geo_type == 'MultiLineString': # dimension = 3
        # example: [
        #            [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],  ==> one polygon
        #            [[20, 30], [35, 35], [30, 20], [20, 30]]             ==> the other
        #           ]
        # find the minmum and maximum values
        the_bounding_box = high_dimension_computation(in_coordinates)
        
    elif geo_type == 'MultiPolygon': # dimension = 4
        multiPoly_bb_list = []
        for polygon_index in range(len(in_coordinates)):
            multiPoly_bb_list.append(high_dimension_computation(in_coordinates[polygon_index]))
        
        the_bounding_box = final_bounding_box_generation(multiPoly_bb_list, 4)
    
    return the_bounding_box
# =======================================
# unwrap complicated geometry types
def unwrap_func(geometries_list, ids_list, flag, file_name):
    # varialbes
    output_list = []
    id_count_index = 0
    geometry_collection_bounding_box_list = []
    
    # iterate through all the "geometrycollection" features in "geometries"
    for ind2 in range(len(geometries_list)):
        # extension calculation and add the extend into a geometry-collection list
        geometry_collection_bounding_box_list.append(min_max_calculation(geometries_list[ind2]['type'], geometries_list[ind2]['coordinates']))
        
        if geometries_list[ind2]['type'] == 'MultiLineString' or geometries_list[ind2]['type'] == 'MultiPoint':
            type_name = ''
            if geometries_list[ind2]['type'] == 'MultiLineString':
                type_name = 'LineString'
            else:
                type_name = 'Point'
            for arry_ind in range(len(geometries_list[ind2]['coordinates'])):
                if len(ids_list[id_count_index + arry_ind]) != 0:
                    output_list.append([type_name, geometries_list[ind2]['coordinates'][arry_ind], flag,
                                        ids_list[id_count_index + arry_ind]['osmid'], ids_list[id_count_index + arry_ind]['ItemId'],
                                        file_name])
            id_count_index += len(geometries_list[ind2]['coordinates'])
        else:  # A point or a line
            if len(ids_list[id_count_index]) != 0:
                output_list.append([geometries_list[ind2]['type'], geometries_list[ind2]['coordinates'], flag,
                                    ids_list[id_count_index]['osmid'], ids_list[id_count_index]['ItemId'], file_name])
            id_count_index += 1
    # =================================================
    return final_bounding_box_generation(geometry_collection_bounding_box_list, 4), output_list
# =======================================
# Find min_X, max_X, min_Y, and max_Y given a Geo-json file or multiple files
def bounding_box_process(in_folder_path):
    output_data = []
    folder_bounding_box_set = []
    name_num_list = []
    name_num_list.append(['Check_name', 'Counts'])
    start_point = 0
    end_point = 0
    roadFile = ''
    
    # check whether or not a road file exists in a sub-directory
    sub_folders = filter(lambda x: os.path.isdir(x), os.listdir(in_folder_path))
    try:
        roadFile = [f for f in os.listdir(os.path.join(in_folder_path, sub_folders[0])) if f.endswith('.geojson')][0]
    except TypeError:
        roadFile = ''
    
    # loop through all geojson files
    for f in os.listdir(in_folder_path):
        # ==========================================
        # load the Geo-json file and ignore other files
        if os.path.splitext(os.path.join(in_folder_path, f))[1] == '.geojson':
            if len(os.path.splitext(f)[0].split('-')) == 3:
                name_num_list.append([os.path.splitext(f)[0].split('-')[0], int(os.path.splitext(f)[0].split('-')[2])])
            
            # open geojson files
            with open(os.path.join(in_folder_path, f), encoding='utf-8') as new_f:
                data = json.load(new_f)

            # randomly generate unique integers (flag ids)
            end_point = start_point + len(data['features'])
            int_array = np.arange(start_point, end_point)
            int_array = np.random.permutation(int_array)
            
            # process all geometries to generate an entire data and multiple geometry bounding boxes
            geometry_bounding_box_list = []
            for index in range(0, len(data['features'])):
                # find a bounding box given a set of coordinates
                # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
                if data['features'][index]['geometry']['type'] == 'GeometryCollection':
                    if len(data['features'][index]['geometry']['geometries']) != 0:
                        # iterates through all elements in "geometries" and find the bounding box
                        geometry_bounding_box, tmp_geometry_collec = unwrap_func(data['features'][index]['geometry']['geometries'],
                                                                            data['features'][index]['properties']['feature_properties'],
                                                                            int_array[index], f)
                        # ==============================
                        geometry_bounding_box_list.append(geometry_bounding_box)
                        output_data = output_data + tmp_geometry_collec
                    # ==============================
                else:
                    # discard a feature without its feature property
                    if len(data['features'][index]['properties']['feature_properties']) != 0:
                        geometry_bounding_box = min_max_calculation(data['features'][index]['geometry']['type'],
                                                              data['features'][index]['geometry']['coordinates'])
                        output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates'],
                                            int_array[index], data['features'][index]['properties']['feature_properties'][0]['osmid'],
                                            data['features'][index]['properties']['feature_properties'][0]['ItemId'], f])
                        geometry_bounding_box_list.append(geometry_bounding_box)
            
            # get a file bounding box for given multiple geometry bounding boxes, and add it into folder bounding box list
            folder_bounding_box_set.append(final_bounding_box_generation(geometry_bounding_box_list, 4))
            del geometry_bounding_box_list
            
            # update start point
            start_point = len(data['features'])

    # get a folder bounding box giving one or more fix bounding box
    final_bounding_box = final_bounding_box_generation(folder_bounding_box_set, 4)
    
    return output_data, final_bounding_box, name_num_list, roadFile
# =======================================
def main():
    # declare variables and arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--folderPath', type = str, default='', help='path to an input folder')

    args = parser.parse_args()
    file_path = args.folderPath

    # find an initial bounding box given all geometries
    entire_data, out_BB, out_name_num, road_file = bounding_box_process(file_path)
    
    # calculate the initial extension area
    obj = {}
    obj['type'] = 'Polygon'
    obj['coordinates'] = [[ [out_BB[0],out_BB[1]],
                            [out_BB[0],out_BB[3]],
                            [out_BB[2],out_BB[3]],
                            [out_BB[2],out_BB[1]] ]]
    
    # write all results to standard output
    out_dic = {}
    out_dic['inFolder'] = file_path
    out_dic['data'] = entire_data
    out_dic['iniBb'] = out_BB
    out_dic['nameNum'] = out_name_num
    out_dic['roadFile'] = road_file
    out_dic['iniArea'] = area(obj)
    
    print(out_dic)
    sys.stdout.flush()
# =======================================
if __name__ == "__main__":
    main()
