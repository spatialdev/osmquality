import numpy as np

class kdTree:
    def __init__(self, tree_depth, bounding_box, data, gridId_start):
        self.root = None
        self.max_depth = tree_depth
        self.initial_bb = bounding_box
        self.data = data
        self.histogram = None
        self.bb_collection= []
        self.gridid_collection = {}
        self.id_start = gridId_start
    # =====================================
    # get a split rule
    def Get_split(self, level_count, in_bb):
        # if the counter is 0 or even numbers, we would like to partition a 2-D region along X-axis
        if level_count == 0 or (level_count & 1) == 0:
            # get a middle value given min_X and max_X
            return {'X_Middle_Value' : in_bb[0] + (in_bb[2] - in_bb[0]) / 2 }
        elif (level_count & 1) == 1:
            # get a middle value given min_Y and max_Y
            return { 'Y_Middle_Value' : in_bb[1] + (in_bb[3] - in_bb[1]) / 2 }
    # =====================================
    # split the bounding box into two boxes
    def BB_split(self, in_node, input_BB, level_value):
        left_up_BB = []
        right_down_BB = []
        if (level_value & 1) == 0 or level_value == 0:
            left_up_BB = [input_BB[0], input_BB[1], input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[3]]
            right_down_BB = [input_BB[0] + (input_BB[2] - input_BB[0]) / 2, input_BB[1], input_BB[2], input_BB[3]] 
        elif (level_value & 1) == 1:
            left_up_BB = [input_BB[0], input_BB[1] + (input_BB[3] - input_BB[1]) / 2, input_BB[2], input_BB[3]]
            right_down_BB = [input_BB[0], input_BB[1], input_BB[2], input_BB[1] + (input_BB[3] - input_BB[1]) / 2] 
        return left_up_BB, right_down_BB
    # =====================================
    # build subtrees
    def build_subtree(self, node, depth_value, input_bb):
        # split the initial bounding box into two bounding boxes
        left_up_bb, right_down_bb = self.BB_split(node, input_bb, depth_value)
        
        # stop conditions
        if depth_value >= self.max_depth:
            node['left'] = left_up_bb 
            # ==========================================================
            node['right'] = right_down_bb 
            return
        
        # process left subtrees
        node['left'] = self.Get_split(depth_value, left_up_bb) # get the split rule
        self.build_subtree(node['left'], depth_value + 1, left_up_bb)
        
        # process right subtrees
        node['right'] = self.Get_split(depth_value, right_down_bb) # get the split rule
        self.build_subtree(node['right'], depth_value + 1, right_down_bb)
        
    # =====================================
    # help function
    def help_fun(self, input_tree, level_val):
        if isinstance(input_tree, dict):
            self.help_fun(input_tree['left'], level_val + 1)
            self.help_fun(input_tree['right'], level_val + 1)
        else:
            self.bb_collection.append(input_tree)
    # =====================================
    # get all leaves
    def get_leaves(self, input_tree):
        # get all leaves
        self.help_fun(input_tree, 0)
        return self.bb_collection
    # =====================================
    def point_within_grid(self, ind, geo_coordinate, bb_coordinate, in_tmp_array, item_id, in_geo):
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
    # =====================================
    # calculate the counts in every cell
    def object_count(self, geo_type, in_coordinates, itemid):
        # ==================================
        if geo_type == 'Point':
            np_array = np.array(in_coordinates)
            # loop through all cells
            for ind in range(len(self.bb_collection)):
                self.point_within_grid(ind, np_array, self.bb_collection[ind], None, itemid, geo_type)
        # ==================================
        elif geo_type == 'LineString':
            np_array = np.array(in_coordinates)
            tmp_array = np.zeros(len(self.bb_collection))
            # loop through all cells
            for ind in range(len(self.bb_collection)):
                for coordinate_ind in range(np_array.shape[0]):
                    self.point_within_grid(ind, np_array[coordinate_ind, :], self.bb_collection[ind], tmp_array, None, None)
            
            #print('temp :', tmp_array)
            tmp_grid_id_list = []
            for ind2 in range(len(self.bb_collection)):
                if tmp_array[ind2] > 0:
                    self.histogram[ind2] += 1
                    tmp_grid_id_list.append(ind2 + self.id_start)                    
            #self.gridid_collection[itemid] = np.nonzero(tmp_array)[0] + self.id_start
            self.gridid_collection[itemid + '-' + geo_type] = tmp_grid_id_list
        # ==================================
    # =====================================
    # calculate the counts in every cell
    def counts_calculation(self):
        self.histogram = np.zeros(len(self.bb_collection))
        
        # loop through each geometry
        for index in range(len(self.data)):
            self.object_count(self.data[index][0], self.data[index][1], self.data[index][4])
            
        return self.histogram, self.gridid_collection
    # =====================================
    # build a 2-d tree
    def tree_building(self):
        # get the split point and start with the root
        self.root = self.Get_split(0, self.initial_bb)
        # build the subtree
        self.build_subtree(self.root, 1, self.initial_bb)
        return self.root

