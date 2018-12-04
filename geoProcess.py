import json
import numpy as np
import sys
import os
from area import area
from utility import Utility
import argparse


class GeoProcessor:
    """ GeoProcessor class.

    This class reads one or more Geo-Json files to parse all of them. The class then
    crafts a nested list with large amounts of important information. For example, the
    important infomration consists of geometry coordinates, geo-types, OSM ids, and etc.
    The class is further able to get a area of an extend and get a road file via
    "get_initial_extend_area" and "get_road_file", respectively.
    
    """
    
    def __init__(self, input_folder_path):
        """ The docstring of the __init__ method.

        Args:
            input_folder_path (str): a folder path to an input directory.
            
        """
        self.folder_path = input_folder_path

        #: list of list: a nested list with some important information.
        self.output_data = []
    
    def __del__(self):
        """ The doctring of the __del__ method.

        write out a message of deleting Utility module to standard error
        
        """
        sys.stderr.write("deling" + str(self) + '\n')
    
    def final_bounding_box_generation(self, input_list, column_length):
        """ Bounding box generation.

        This method generates a final bounding box.

        Args:
            input_list: a collection of geometry coordinates.
            column_length: column length of an input 2-dimensional matrix.
            
        Returns:
            [x_min, y_min, x_max, y_max]: a bounding box
        
        """
        x_min = x_max = y_min = y_max = 0

        
        if column_length == 4:
            np_geometry_bounding_box_list = np.asarray(input_list)
            _, _, x_max, y_max = np_geometry_bounding_box_list.max(axis = 0)
            x_min, y_min, _, _ = np_geometry_bounding_box_list.min(axis = 0)
            
        elif column_length == 2:
            x_max, y_max = input_list.max(axis = 0)
            x_min, y_min = input_list.min(axis = 0)

        
        return [x_min, y_min, x_max, y_max]
    
    def high_dimension_computation(self, in_matrix):
        """ High dimension computation.

        This method is to find a bounding box from a high dimensional matrix.

        Args:
            in_matrix: a collection of geometry coordinates.

        Returns:
            self.final_bounding_box_generation(storage_list, 4): a bounding box.
            
        """
        storage_list = []

        
        for list_index in range(len(in_matrix)):
            storage_list.append(self.final_bounding_box_generation(np.array(in_matrix[list_index]), 2))

        
        return self.final_bounding_box_generation(storage_list, 4)
    
    def min_max_calculation(self, geo_type, in_coordinates):
        """ Minimum and Maximum Calculation.

        This method finds the minimum and maximum for a given geometry.

        Args:
            geo_type: a geometry type
            in_coordinates: a geometry with its coordinates.

        Returns:
            the_bounding_box: a bounding box.
            
        Examples:
            A polygon geo-type or a multiLineString geo-type:
            [
              [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],  ==> one polygon
              [[20, 30], [35, 35], [30, 20], [20, 30]]             ==> the other
            ]
        
        """
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
                the_bounding_box = self.final_bounding_box_generation(np_array, 2)
                
        elif geo_type == 'Polygon' or geo_type == 'MultiLineString':
            # find the minmum and maximum values
            the_bounding_box = self.high_dimension_computation(in_coordinates)
            
        elif geo_type == 'MultiPolygon':
            multiPoly_bb_list = []

            for polygon_index in range(len(in_coordinates)):
                multiPoly_bb_list.append(self.high_dimension_computation(in_coordinates[polygon_index]))

            the_bounding_box = self.final_bounding_box_generation(multiPoly_bb_list, 4)
        
            
        return the_bounding_box
    
    def unwrap_func(self, geometries_list, ids_list, flag, file_name):
        """ Unwrapper function.

        This method is to unwrap complicated geometry types to extract simple geometries from a collection of geometries.

        Args:
            geometries_list: a collection of geometries.
            ids_list: a collection of OSM ids.
            flag: a artificial flag.
            file_name: a file name.
            
        Returns:
            self.final_bounding_box_generation(geometry_collection_bounding_box_list, 4): a bounding box.
            output_list: a nested list with some important information. For example, geo-type, geometry coordinates, etc.
        
        """
        # varialbes
        output_list = []
        id_count_index = 0
        geometry_collection_bounding_box_list = []

        
        # iterate through all the "geometrycollection" features in "geometries"
        for geometry_collec_index in range(len(geometries_list)):
            # extension calculation and add the extend into a geometry-collection list
            geometry_collection_bounding_box_list.append(self.min_max_calculation(geometries_list[geometry_collec_index]['type'],
                                                                                  geometries_list[geometry_collec_index]['coordinates']))
            
            if geometries_list[geometry_collec_index]['type'] == 'MultiLineString' or geometries_list[geometry_collec_index]['type'] == 'MultiPoint':
                type_name = ''
                if geometries_list[geometry_collec_index]['type'] == 'MultiLineString':
                    type_name = 'LineString'
                    
                else:
                    type_name = 'Point'

                for arry_ind in range(len(geometries_list[geometry_collec_index]['coordinates'])):
                    if len(ids_list[id_count_index + arry_ind]) != 0:
                        output_list.append([type_name, geometries_list[geometry_collec_index]['coordinates'][arry_ind], flag,
                                            ids_list[id_count_index + arry_ind]['osmid'], ids_list[id_count_index + arry_ind]['ItemId'],
                                            file_name])
                
                id_count_index += len(geometries_list[geometry_collec_index]['coordinates'])
                
            else: # a point, a line, a polygon, or a multi-polygon
                if len(ids_list[id_count_index]) != 0:
                    output_list.append([geometries_list[geometry_collec_index]['type'], geometries_list[geometry_collec_index]['coordinates'], flag,
                                        ids_list[id_count_index]['osmid'], ids_list[id_count_index]['ItemId'], file_name])
                id_count_index += 1
        # =================================================

        
        return self.final_bounding_box_generation(geometry_collection_bounding_box_list, 4), output_list
    
    def bounding_box_process(self):
        """ Bounding box generation.

        This method finds min_X, max_X, min_Y, and max_Y for a given Geo-json file or multiple files.

        Returns:
            self.output_data: a nested list with some important information.
            final_bounding_box: an initial bounding box.
            name_num_list: a two-dimensional list with check names and the number of counts.
        
        """
        folder_bounding_box_set = []
        name_num_list = []
        name_num_list.append(['Check_name', 'Counts'])
        start_point = 0
        end_point = 0

        
        # loop through all geojson files
        for f in os.listdir(self.folder_path):
            # load the Geo-json file and ignore other files
            if os.path.splitext(os.path.join(self.folder_path, f))[1] == '.geojson':
                if len(os.path.splitext(f)[0].split('-')) == 3:    # pull out this function
                    name_num_list.append([os.path.splitext(f)[0].split('-')[0], int(os.path.splitext(f)[0].split('-')[2])])

                # open geojson files
                with open(os.path.join(self.folder_path, f), encoding='utf-8') as new_f:
                    data = json.load(new_f)

                # randomly generate unique integers (flag ids)
                end_point = start_point + len(data['features'])
                int_array = np.arange(start_point, end_point)
                int_array = np.random.permutation(int_array)

                # process all geometries to generate an entire data and multiple geometry bounding boxes
                geometry_bounding_box_list = []
                for geometry_index in range(len(data['features'])):
                    # find a bounding box given a set of coordinates
                    # determine whether or not the input type is geometrycollection. If so, invoke an unwrap function
                    if data['features'][geometry_index]['geometry']['type'] == 'GeometryCollection':
                        # iterates through all elements in "geometries" and find the bounding box
                        geometry_bounding_box, tmp_geometry_collec = self.unwrap_func(data['features'][geometry_index]['geometry']['geometries'],
                                                                                      data['features'][geometry_index]['properties']['feature_properties'],
                                                                                      int_array[geometry_index], f)
                        # ==============================
                        geometry_bounding_box_list.append(geometry_bounding_box)
                        self.output_data += tmp_geometry_collec
                    
                    else:
                        # discard a feature without feature properties
                        if len(data['features'][geometry_index]['properties']['feature_properties']) != 0:
                            geometry_bounding_box = self.min_max_calculation(data['features'][geometry_index]['geometry']['type'],
                                                                        data['features'][geometry_index]['geometry']['coordinates'])

                            self.output_data.append([data['features'][geometry_index]['geometry']['type'],
                                                     data['features'][geometry_index]['geometry']['coordinates'], int_array[geometry_index],
                                                     data['features'][geometry_index]['properties']['feature_properties'][0]['osmid'],   # here is a problem...
                                                     data['features'][geometry_index]['properties']['feature_properties'][0]['ItemId'], f])   # here is a problem...

                            geometry_bounding_box_list.append(geometry_bounding_box)
                    
                # get a file bounding box for given multiple geometry bounding boxes, and add it into folder bounding box list
                folder_bounding_box_set.append(self.final_bounding_box_generation(geometry_bounding_box_list, 4))
                del geometry_bounding_box_list
                
                # update start point
                start_point = len(data['features'])

        
        # get a folder bounding box giving one or more fix bounding box
        final_bounding_box = self.final_bounding_box_generation(folder_bounding_box_set, 4)

        
        return self.output_data, final_bounding_box, name_num_list
    
    def get_initial_extend_area(self, input_extend):
        """ Initial area calculation.

        This method calculates an area for a given an initial extend.

        Args:
            input_extend: a bounding box.

        Returns:
            area(obj): an area of the initial extend.
        
        """
        # calculate the initial extension area
        obj = {}
        obj['type'] = 'Polygon'
        obj['coordinates'] = [[ [input_extend[0],input_extend[1]],
                                [input_extend[0],input_extend[3]],
                                [input_extend[2],input_extend[3]],
                                [input_extend[2],input_extend[1]] ]]

        
        return area(obj)
    
    def get_road_file(self):
        """ Road file generation.

        This method checks whether or not the folder has a sub-directory and checks that the sub-directory has a road file or not.

        Returns:
            os.path.join(os.path.join(self.folder_path, sub_folder[0]), road_file_name) or '': a file path to the road file.
        
        """
        # check whether or not a road file exists in a sub-directory
        uti = Utility()
        sub_folder = uti.get_sub_directionaries(self.folder_path)

        
        if sub_folder:
            road_file_name = [f for f in os.listdir(os.path.join(self.folder_path, sub_folder[0])) if f.endswith('.geojson')][0]
            return os.path.join(os.path.join(self.folder_path, sub_folder[0]), road_file_name)
        
        else:
            return ''
    
