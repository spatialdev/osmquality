import json
import numpy as np
import sys, os
from area import area
import argparse

def update_function(old_value, new_value, flag):
    if flag == 0:
        if new_value < old_value:
            return new_value
        else:
            return old_value
    elif flag == 1:
        if new_value > old_value:
            return new_value
        else:
            return old_value
# =======================================
def dim_3_computation(in_matrix):
    out_min_X = np.min(np.array(in_matrix[0])[:, 0])
    out_max_X = np.max(np.array(in_matrix[0])[:, 0])
    out_min_Y = np.min(np.array(in_matrix[0])[:, 1])
    out_max_Y = np.max(np.array(in_matrix[0])[:, 1])
    
    for ind in range(len(in_matrix)):
        if ind == 0:
            continue
        # update the values
        out_min_X = update_function(out_min_X, np.min(np.array(in_matrix[ind])[:, 0]), 0)
        out_max_X = update_function(out_max_X, np.max(np.array(in_matrix[ind])[:, 0]), 1)
        out_min_Y = update_function(out_min_Y, np.min(np.array(in_matrix[ind])[:, 1]), 0)
        out_max_Y = update_function(out_max_Y, np.max(np.array(in_matrix[ind])[:, 1]), 1)

    return out_min_X, out_max_X, out_min_Y, out_max_Y
# =======================================
def min_max_calculation(geo_type, in_coordinates):
    # declare variables
    tmp_min_X = tmp_max_X = tmp_min_Y = tmp_max_Y = None
    # find the minimum and maximum value based on geometry types
    if geo_type == 'Point' or geo_type == 'LineString' or geo_type == 'MultiPoint':
        np_array = np.array(in_coordinates)
        dim_value = len(np_array.shape)
        if dim_value == 1:
            # find the minimum and maximum value directly
            tmp_min_X = tmp_max_X = np_array[0]
            tmp_min_Y = tmp_max_Y = np_array[1]
        elif dim_value == 2:
            # find the minimum and maximum values through comparing all elements in individual columns
            tmp_min_X = np.min(np_array[:, 0])
            tmp_max_X = np.max(np_array[:, 0])
            tmp_min_Y = np.min(np_array[:, 1])
            tmp_max_Y = np.max(np_array[:, 1])
    elif geo_type == 'Polygon' or geo_type == 'MultiLineString': # dimension = 3
        # example: [
       #            [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],  ==> one polygon
       #            [[20, 30], [35, 35], [30, 20], [20, 30]]             ==> the other
       #           ]
       # find the minmum and maximum values
        tmp_min_X, tmp_max_X, tmp_min_Y, tmp_max_Y = dim_3_computation(in_coordinates)
    elif geo_type == 'MultiPolygon': # dimension = 4
        for inds in range(len(in_coordinates)):
            if inds == 0:
                tmp_min_X, tmp_max_X, tmp_min_Y, tmp_max_Y = dim_3_computation(in_coordinates[inds])
            else:
                min_x, max_x, min_y, max_y = dim_3_computation(in_coordinates[inds])
                # update the values
                tmp_min_X = update_function(tmp_min_X, min_x, 0)
                tmp_max_X = update_function(tmp_max_X, max_x, 1)
                tmp_min_Y = update_function(tmp_min_Y, min_y, 0)
                tmp_max_Y = update_function(tmp_max_Y, max_y, 1)
    
    return [tmp_min_X, tmp_min_Y, tmp_max_X, tmp_max_Y]
# =======================================
# unwrap complicated geometry types
def unwrap_func(geometries_list, ids_list, flag, file_name):
    
    # process the first "geometrycollection" feature,
    # extension calculation
    tmp_storage_list = []
    id_count_index = 0
    tmp = min_max_calculation(geometries_list[0]['type'], geometries_list[0]['coordinates'])
    # split mixed geometries to multiple individual geometries when the type is MultiPoint or MultiLineString
    if geometries_list[0]['type'] == 'MultiLineString' or geometries_list[0]['type'] == 'MultiPoint':
        type_name = ''
        if geometries_list[0]['type'] == 'MultiLineString':
            type_name = 'LineString'
        else:
            type_name = 'Point'
        for arry_ind in range(len(geometries_list[0]['coordinates'])):
            if len(ids_list[id_count_index + arry_ind]) != 0:
                tmp_storage_list.append([type_name, geometries_list[0]['coordinates'][arry_ind], flag, ids_list[id_count_index + arry_ind]['osmid'],
                                         ids_list[id_count_index + arry_ind]['ItemId'], file_name])
        id_count_index += len(geometries_list[0]['coordinates'])
    else:  # A point or a line
        if len(ids_list[id_count_index]) != 0:
            tmp_storage_list.append([geometries_list[0]['type'], geometries_list[0]['coordinates'], flag, ids_list[id_count_index]['osmid'],
                                     ids_list[id_count_index]['ItemId'], file_name])
        id_count_index += 1
    # iterates through the remaining "geometrycollection" features in "geometries"  it is also a list.
    for ind2 in range(len(geometries_list)):
        if ind2 == 0:
            continue
        else:
            # extension calculation
            tmp2 = min_max_calculation(geometries_list[ind2]['type'], geometries_list[ind2]['coordinates'])

            if geometries_list[ind2]['type'] == 'MultiLineString' or geometries_list[ind2]['type'] == 'MultiPoint':
                type_name = ''
                if geometries_list[ind2]['type'] == 'MultiLineString':
                    type_name = 'LineString'
                else:
                    type_name = 'Point'
                for arry_ind in range(len(geometries_list[ind2]['coordinates'])):
                    if len(ids_list[id_count_index + arry_ind]) != 0:
                        tmp_storage_list.append([type_name, geometries_list[ind2]['coordinates'][arry_ind], flag,
                                                 ids_list[id_count_index + arry_ind]['osmid'], ids_list[id_count_index + arry_ind]['ItemId'],
                                                 file_name])
                id_count_index += len(geometries_list[ind2]['coordinates'])
            else:  # A point or a line
                if len(ids_list[id_count_index]) != 0:
                    tmp_storage_list.append([geometries_list[ind2]['type'], geometries_list[ind2]['coordinates'], flag,
                                             ids_list[id_count_index]['osmid'], ids_list[id_count_index]['ItemId'], file_name])
                id_count_index += 1
            # update the bounding box
            tmp[0] = update_function(tmp[0], tmp2[0], 0)
            tmp[1] = update_function(tmp[1], tmp2[1], 0)
            tmp[2] = update_function(tmp[2], tmp2[2], 1)
            tmp[3] = update_function(tmp[3], tmp2[3], 1)
    # =================================================
    return tmp, tmp_storage_list
# =======================================
# Find min_X, max_X, min_Y, and max_Y given a Geo-json file or multiple files
def bounding_box_process(in_folder_path):
    output_data = []
    bounding_box_set = []
    bounding_box = None
    name_num_list = []
    name_num_list.append(['Check_name', 'Counts'])
    start_point = 0
    end_point = 0
    roadFile = ''
    
    # loop through all geojson files
    for f in os.listdir(in_folder_path):
        # ==========================================
        if os.path.isdir(os.path.join(in_folder_path, f)):
            for subdir, dirs, files in os.walk(os.path.join(in_folder_path, f)):
                for file in files:
                    filepath = subdir + os.sep + file

                    if filepath.endswith('.geojson'):
                        roadFile = filepath
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

            # find the minimum and maximum values of the 1st set of coordinates
            # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
            if data['features'][0]['geometry']['type'] == 'GeometryCollection':
                # iterates through all elements in "geometries" and find the bounding box
                if len(data['features'][0]['geometry']['geometries']) != 0:
                    bounding_box, geometry_collec = unwrap_func(data['features'][0]['geometry']['geometries'],
                                                                data['features'][0]['properties']['feature_properties'],
                                                                int_array[0], f)
                    # ==============================
                    output_data = output_data + geometry_collec
                # ==============================
            else:
                # discard a feature without its feature property
                if len(data['features'][0]['properties']['feature_properties']) != 0:
                    bounding_box = min_max_calculation(data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'])
                    output_data.append([data['features'][0]['geometry']['type'], data['features'][0]['geometry']['coordinates'],
                                        int_array[0], data['features'][0]['properties']['feature_properties'][0]['osmid'],
                                        data['features'][0]['properties']['feature_properties'][0]['ItemId'], f])

            # process all geometries excluding the 1st one
            for index in range(1, len(data['features'])):
                # find a bounding box given a set of coordinates
                # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
                if data['features'][index]['geometry']['type'] == 'GeometryCollection':
                    if len(data['features'][index]['geometry']['geometries']) != 0:
                        # iterates through all elements in "geometries" and find the bounding box
                        tmp_bounding_box, tmp_geometry_collec = unwrap_func(data['features'][index]['geometry']['geometries'],
                                                                            data['features'][index]['properties']['feature_properties'],
                                                                            int_array[index], f)
                        # ==============================
                        output_data = output_data + tmp_geometry_collec
                    # ==============================
                else:
                    # discard a feature without its feature property
                    if len(data['features'][index]['properties']['feature_properties']) != 0:
                        tmp_bounding_box= min_max_calculation(data['features'][index]['geometry']['type'],
                                                              data['features'][index]['geometry']['coordinates'])
                        output_data.append([data['features'][index]['geometry']['type'], data['features'][index]['geometry']['coordinates'],
                                            int_array[index], data['features'][index]['properties']['feature_properties'][0]['osmid'],
                                            data['features'][index]['properties']['feature_properties'][0]['ItemId'], f])
                # update the minimum and maximum values
                bounding_box[0] = update_function(bounding_box[0], tmp_bounding_box[0], 0)
                bounding_box[1] = update_function(bounding_box[1], tmp_bounding_box[1], 0)
                bounding_box[2] = update_function(bounding_box[2], tmp_bounding_box[2], 1)
                bounding_box[3] = update_function(bounding_box[3], tmp_bounding_box[3], 1)
            bounding_box_set.append(bounding_box)

            # update start point
            start_point = len(data['features'])
    
    return output_data, bounding_box_set, name_num_list, roadFile
# =======================================
def main():
    # declare variables and arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--folderPath', type = str, default='', help='path to an input folder')

    args = parser.parse_args()
    file_path = args.folderPath

    # find an initial bounding box given all geometries
    final_BB = None
    entire_data, out_BB, out_name_num, road_file = bounding_box_process(file_path)

    if len(out_BB) == 1:
        final_BB = out_BB[0]
    else:
        final_BB = out_BB[0]
        for index in range(len(out_BB)):
            # skip the 1st one
            if index == 0:
                continue
            final_BB[0] = update_function(final_BB[0], out_BB[index][0], 0)
            final_BB[1] = update_function(final_BB[1], out_BB[index][1], 0)
            final_BB[2] = update_function(final_BB[2], out_BB[index][2], 1)
            final_BB[3] = update_function(final_BB[3], out_BB[index][3], 1)

    # calculate the initial extension area
    obj = {}
    obj['type'] = 'Polygon'
    obj['coordinates'] = [[ [final_BB[0],final_BB[1]],
                            [final_BB[0],final_BB[3]],
                            [final_BB[2],final_BB[3]],
                            [final_BB[2],final_BB[1]] ]]
    
    # write all results to standard output
    out_dic = {}
    out_dic['inFolder'] = file_path
    out_dic['data'] = entire_data
    out_dic['iniBb'] = final_BB
    out_dic['nameNum'] = out_name_num
    out_dic['roadFile'] = road_file
    out_dic['iniArea'] = area(obj)
    
    print(out_dic)
    sys.stdout.flush()
# =======================================
if __name__ == "__main__":
    main()
