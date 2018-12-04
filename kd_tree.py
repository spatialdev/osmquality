import numpy as np


class kdTree:
    """ kdTree class.
    
    This class contains several essential functions to build a k-d tree and travel the tree for grabbing all of the tree leaves.
    
    """
    
    def __init__(self, tree_depth, bounding_box, data, gridId_start):
        """ The docstring of the __init__ method.

        Args:
            tree_depth (int): tree depth for the k-d tree.
            bounding_box (:obj:`list`): a bounding box list with X_min, X_max, Y_min, and Y_max.
            data (:obj:`list` of :obj:`list`): a nested list with some important information.
            gridId_start (int): a start grid id.
            
        """
        self.max_depth = tree_depth
        self.initial_bb = bounding_box
        self.data = data
        self.id_start = gridId_start

        #: list of list: a collection of bounding boxes.
        self.bb_collection = []
        
        #: dictionary: a collection of pairs of an item id plus a geometry type and a list of grid ids.
        self.gridid_collection = {}

        self.histogram = None
        """numpy array: a one-dimensional numpy array to store the number of flagged features in each grid."""
        
        self.root = None
        """dict: a k-d tree."""
        
    def Get_split(self, level_count, in_bb):
        """ Split method.

        This method is to get a split rule.

        Args:
            level_count: tree level that starts from 0.
            in_bb: a bounding-box list.

        Returns:
            {'X_Middle_Value' : in_bb[0] + (in_bb[2] - in_bb[0]) / 2 }: a pair value for X-axis.
            { 'Y_Middle_Value' : in_bb[1] + (in_bb[3] - in_bb[1]) / 2 }: a pair value for Y-axis.
            
        """
        # if the counter is 0 or even numbers, we would like to partition a 2-D region along X-axis
        if level_count == 0 or (level_count & 1) == 0:
            # get a middle value given min_X and max_X
            return {'X_Middle_Value' : in_bb[0] + (in_bb[2] - in_bb[0]) / 2 }
        
        elif (level_count & 1) == 1:
            # get a middle value given min_Y and max_Y
            return { 'Y_Middle_Value' : in_bb[1] + (in_bb[3] - in_bb[1]) / 2 }
        
    def BB_split(self, input_BB, level_value):
        """ Bounding-box split method.

        The method splits the bounding box to two boxes based on X-axis or Y-axis.

        Args:
            input_BB: a bounding-box list.
            level_value: tree level that starts from 0.
        
        Returns:
            left_up_BB: either a left bounding box or a up bounding box.
            right_down_BB: either a right bounding box or a down bounding box.
            
        """
        left_up_BB = []
        right_down_BB = []

        
        if (level_value & 1) == 0 or level_value == 0:
            left_up_BB = [input_BB[0], input_BB[1], input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[3]]
            right_down_BB = [input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[1], input_BB[2], input_BB[3]]
            
        elif (level_value & 1) == 1:
            left_up_BB = [input_BB[0], input_BB[1] + (input_BB[3] - input_BB[1]) / 2, input_BB[2], input_BB[3]]
            right_down_BB = [input_BB[0], input_BB[1], input_BB[2], input_BB[1] + (input_BB[3] - input_BB[1]) / 2]

        
        return left_up_BB, right_down_BB
    
    def build_subtree(self, node, depth_value, input_bb):
        """ Subtree build method.

        This method builds subtrees recursively.

        Args:
            node: a tree node.
            depth_value: a tree level.
            input_bb: a bounding-box list.
            
        """
        # split the initial bounding box into two bounding boxes
        left_up_bb, right_down_bb = self.BB_split(input_bb, depth_value)

        
        # stop conditions
        if depth_value >= self.max_depth:
            node['left'] = left_up_bb
            node['right'] = right_down_bb 
            return
        
        
        # process left subtrees
        node['left'] = self.Get_split(depth_value, left_up_bb) # get the split rule
        self.build_subtree(node['left'], depth_value + 1, left_up_bb)

        
        # process right subtrees
        node['right'] = self.Get_split(depth_value, right_down_bb) # get the split rule
        self.build_subtree(node['right'], depth_value + 1, right_down_bb)
        
    def tree_travel(self, input_tree, level_val):
        """ Tree travel method.

        This method travels the entire k-d tree recursively.

        Args:
            input_tree: a k-d tree.
            level_val: a tree level.
            
        """
        if isinstance(input_tree, dict):
            self.tree_travel(input_tree['left'], level_val + 1)
            self.tree_travel(input_tree['right'], level_val + 1)
            
        else:
            self.bb_collection.append(input_tree)
            
    def get_leaves(self, input_tree):
        """ Leaves grabbing method.

        This method gets all of the tree leaves from the k-d tree.

        Args:
            input_tree: a k-d tree.
            
        Returns:
            self.bb_collection: a collection of all the bounding boxes.
            
        """        
        # get all leaves
        self.tree_travel(input_tree, 0)
        return self.bb_collection
    
    def point_within_grid(self, ind, geo_coordinate, bb_coordinate, in_tmp_array, item_id, in_geo):
        """ Check coordinate method.

        This method checks whether or not a coordinate is in a grid.
        
        Args:
            ind: an index value.
            geo_coordinate: a coordinate for a geometry.
            bb_coordinate: a bounding box.
            in_tmp_array: a temp array to record the number of geometries inside a grid.
            item_id: an item id.
            in_geo: a geometry type.
            
        """
        if self.bb_collection[ind][3] == self.initial_bb[3] and self.bb_collection[ind][2] == self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] <= bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] <= bb_coordinate[3]):

                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                    
                else:
                    self.histogram[ind] += 1
                    self.gridid_collection[item_id + '-' + in_geo] = ind + self.id_start
                    
        elif self.bb_collection[ind][3] == self.initial_bb[3] and self.bb_collection[ind][2] != self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] < bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] <= bb_coordinate[3]):

                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                    
                else:
                    self.histogram[ind] += 1
                    self.gridid_collection[item_id + '-' + in_geo] = ind + self.id_start
                    
        elif self.bb_collection[ind][3] != self.initial_bb[3] and self.bb_collection[ind][2] == self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] <= bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] < bb_coordinate[3]):

                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                    
                else:
                    self.histogram[ind] += 1
                    self.gridid_collection[item_id + '-' + in_geo] = ind + self.id_start
                    
        elif self.bb_collection[ind][3] != self.initial_bb[3] and self.bb_collection[ind][2] != self.initial_bb[2]:
            if (geo_coordinate[0] >= bb_coordinate[0] and geo_coordinate[0] < bb_coordinate[2] and
                geo_coordinate[1] >= bb_coordinate[1] and geo_coordinate[1] < bb_coordinate[3]):

                if not (in_tmp_array is None):
                    in_tmp_array[ind] += 1
                    
                else:
                    self.histogram[ind] += 1
                    self.gridid_collection[item_id + '-' + in_geo] = ind + self.id_start
                    
    def counting_function(self, in_coordinates):
        """ A counting function for a geometry.

        This method calculates the number of counts for a given geometry.

        Args:
            in_coordinates: a geometry with its coordinates.
            
        Returns:
            tmp_grid_id_list: a grid-id list.
            
        """
        np_array = np.array(in_coordinates)
        tmp_array = np.zeros(len(self.bb_collection))
        tmp_grid_id_list = []

        
        # loop through all cells
        for ind in range(len(self.bb_collection)):
            for coordinate_ind in range(np_array.shape[0]):
                self.point_within_grid(ind, np_array[coordinate_ind, :], self.bb_collection[ind], tmp_array, None, None)
        
        
        for ind2 in range(len(self.bb_collection)):
            if tmp_array[ind2] > 0:
                self.histogram[ind2] += 1
                tmp_grid_id_list.append(ind2 + self.id_start)
        
        
        return tmp_grid_id_list
    
    def object_count(self, geo_type, in_coordinates, itemid):
        """ Object count method.

        The method calculates the counts and creates a grid-id list.

        Args:
            geo_type: a geometry type.
            in_coordinates: a geometry with its coordinates.
            itemid: an item id.
            
        """
        if geo_type == 'Point':
            np_array = np.array(in_coordinates)
            # loop through all cells
            for ind in range(len(self.bb_collection)):
                self.point_within_grid(ind, np_array, self.bb_collection[ind], None, itemid, geo_type)
        
        elif geo_type == 'LineString':
            self.gridid_collection[itemid + '-' + geo_type] = self.counting_function(in_coordinates)
        
        elif geo_type == 'Polygon':
            polygon_ids_list = []
            # iterate through all polygons
            for polygon_index in range(len(in_coordinates)):
                polygon_ids_list += self.counting_function(in_coordinates[polygon_index])
            
            self.gridid_collection[itemid + '-' + geo_type] = polygon_ids_list
        
        elif geo_type == 'MultiPolygon':
            multi_polygon_ids_list = []
            for polygon_ind in range(len(in_coordinates)):
                # get single polygon
                for single_polygon_index in range(len(in_coordinates[polygon_ind])):
                    multi_polygon_ids_list += self.counting_function(in_coordinates[polygon_ind][single_polygon_index])
            
            self.gridid_collection[itemid + '-' + geo_type] = multi_polygon_ids_list
            
    def counts_calculation(self):
        """ Counts calculation function.

        This method calculates the counts in every grid.

        Returns:
            self.histogram: a count list.
            self.gridid_collection: a grid-id list.
            
        """
        self.histogram = np.zeros(len(self.bb_collection))

        
        # loop through each geometry
        for index in range(len(self.data)):
            self.object_count(self.data[index][0], self.data[index][1], self.data[index][4])

        
        return self.histogram, self.gridid_collection
    
    def tree_building(self):
        """ Tree building method.

        The method is to build 2-d tree.

        Returns:
            self.root: a 2-d tree.
            
        """
        # get the split point and start with the root
        self.root = self.Get_split(0, self.initial_bb)

        
        # build the subtree
        self.build_subtree(self.root, 1, self.initial_bb)

        
        return self.root

