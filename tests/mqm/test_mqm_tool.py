import mqm
import pytest
import os


def test_import():
    assert mqm.road_count is not None

""" Stop Condition Testing 
 
 Args:
        count_zero_list: a pair to the number of grids with zero flagged feature.
        count_list: a list to the number of flagged features.
        grid_percent: a percentage value for grids.
        count_num: a count number for a stop condition in the first k-d tree.
        cell_num: the number of keys in the dictionary.
        out_distribution: a dictionary in which key and value represent the number of flagged features and counts, respectively.

    Returns: stop_flag =True or False
"""


def test_default_stop_condition():
    out_distribution_1 = {3.0: 2, 10.0: 1, 65.0: 1, 77.0: 1, 102.0: 1}
    count_zero_list_1 = [0, 2]
    count_list_1 = [13.0, 65.0, 179.0]
    test_case_1 = mqm.stop_condition(count_zero_list_1, count_list_1, 0.9, 10, 5, out_distribution_1)
    assert test_case_1 == False

    out_distribution_2 = {2.0: 4, 3.0: 3, 4.0: 7, 5.0: 1, 6.0: 1, 8.0: 1, 9.0: 2, 10.0: 2, 11.0: 1, 13.0: 1, 18.0: 1,
                          19.0: 1, 20.0: 1, 23.0: 1, 31.0: 2}
    count_zero_list_2 = [0, 99]
    count_list_2 = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 11.0, 13.0, 18.0, 19.0, 20.0, 23.0, 31.0]
    test_case_2 = mqm.stop_condition(count_zero_list_2, count_list_2, 0.9, 10, 15, out_distribution_2)
    assert test_case_2 == True


def test_percentage_stop_condition():
    out_distribution_3 = {2.0: 4, 3.0: 3, 4.0: 7, 5.0: 1, 6.0: 1, 8.0: 1, 9.0: 2, 10.0: 2, 11.0: 1, 13.0: 1, 18.0: 1,
                          19.0: 1, 20.0: 1, 23.0: 1, 31.0: 2}
    count_zero_list_3 = [0, 99]
    count_list_3 = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 11.0, 13.0, 18.0, 19.0, 20.0, 23.0, 31.0]
    test_case_3 = mqm.stop_condition(count_zero_list_3, count_list_3, 0.95, 10, 15, out_distribution_3)
    assert test_case_3 == False

    out_distribution_4 = {2.0: 7, 3.0: 7, 4.0: 8, 5.0: 2, 7.0: 2, 8.0: 2, 9.0: 1, 10.0: 1, 11.0: 1, 16.0: 1, 18.0: 1,
                          20.0: 1, 21.0: 1, 31.0: 2}
    count_zero_list_4 = [0, 219]
    count_list_4 = [2.0, 3.0, 4.0, 5.0, 7.0, 8.0, 9.0, 10.0, 11.0, 16.0, 18.0, 20.0, 21.0, 31.0]
    test_case_4 = mqm.stop_condition(count_zero_list_4, count_list_4, 0.95, 10, 15, out_distribution_4)
    assert test_case_4 == True


def test_min_counts_stop_condition():
    out_distribution_5 = {2.0: 4, 3.0: 3, 4.0: 7, 5.0: 1, 6.0: 1, 8.0: 1, 9.0: 2, 10.0: 2, 11.0: 1, 13.0: 1, 18.0: 1,
                          19.0: 1, 20.0: 1, 23.0: 1, 31.0: 2}
    count_zero_list_5 = [0, 99]
    count_list_5 = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 11.0, 13.0, 18.0, 19.0, 20.0, 23.0, 31.0]
    test_case_5 = mqm.stop_condition(count_zero_list_5, count_list_5, 0.9, 5, 15, out_distribution_5)
    assert test_case_5 == False

    out_distribution_6 = {2.0: 7, 3.0: 7, 4.0: 8, 5.0: 2, 7.0: 2, 8.0: 2, 9.0: 1, 10.0: 1, 11.0: 1, 16.0: 1, 18.0: 1,
                          20.0: 1, 21.0: 1, 31.0: 2}
    count_zero_list_6 = [0, 219]
    count_list_6 = [2.0, 3.0, 4.0, 5.0, 7.0, 8.0, 9.0, 10.0, 11.0, 16.0, 18.0, 20.0, 21.0, 31.0]
    test_case_6 = mqm.stop_condition(count_zero_list_6, count_list_6, 0.9, 5, 15, out_distribution_6)
    assert test_case_6 == True
