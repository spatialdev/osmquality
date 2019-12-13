import mqm
import os
import pytest


def test_initialize():
    initialized = mqm.Utility()
    assert initialized is not None


def test_histogram_fixtures(tmp_path):
    """
    Verify that matplotlib creates a histogram based on inputs
    Args:
        tmp_path: The pytest tmp_path fixture
    """
    util = mqm.Utility()
    directory = create_temp_directory(tmp_path)
    file_name = directory / "histogram.png"

    stats = {400: 1, 500: 1}
    x_axis = [0, 5]
    util.plot_histogram_figures(file_name, stats, x_axis)

    assert len(list(directory.iterdir())) == 1


def create_temp_directory(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()

    return d


# test distribution_computation


def test_csv_writer(tmp_path):
    """
    Verify that the csv writer creates a file with the correct contents
    Args:
        tmp_path: The pytest tmp_path fixture
    """
    util = mqm.Utility()
    output_directory = create_temp_directory(tmp_path)
    output_path = output_directory / "test.csv"
    data = [
        ['col1', 'col2'],
        ['val1', 'val2']
    ]

    util.csv_writer(data, output_path)

    assert len(list(output_directory.iterdir())) == 1
    assert output_path.read_text().splitlines() == ['col1,col2', 'val1,val2']


def test_road_summary_table_generation(tmp_path):
    util = mqm.Utility()
    output_directory = create_temp_directory(tmp_path)
    output_path = output_directory / "summary_test.csv"
    flag_counts = [
        ['col1', 'col2'],
        ['val1', 20]
    ]
    input_data = [
        ["LineString", [
            [103.9743335, 1.3181635],
            [103.974285, 1.3181588],
            [103.9742448, 1.3181863],
            [103.9742317, 1.3182333],
            [103.9742518, 1.3182776],
            [103.9742958, 1.3182987],
            [103.974343, 1.3182866],
            [103.9743714, 1.3182469],
            [103.9743676, 1.3181984],
            [103.9743335, 1.3181635]
        ], 19, "452036576", "452036576000001", "RoundaboutValenceCheck-1564728254627-38.geojson"],
        ["LineString", [
            [103.9746252, 1.318576],
            [103.9746562, 1.3185682],
            [103.9746824, 1.3185498],
            [103.9747003, 1.3185232],
            [103.9747073, 1.3184919],
            [103.9747026, 1.3184602],
            [103.9746868, 1.3184323]
        ], 27, "526572619", "526572619000001", "RoundaboutValenceCheck-1564728254627-38.geojson"],
        ["LineString", [
            [103.9746252, 1.318576],
            [103.9746562, 1.3185682],
            [103.9746824, 1.3185498],
            [103.9747003, 1.3185232],
            [103.9747073, 1.3184919],
            [103.9747026, 1.3184602],
            [103.9746868, 1.3184323]
        ], 27, "452036576", "452036576000002", "RoundaboutValenceCheck-1564728254627-38.geojson"]

    ]

    table = util.summary_table_row_generation(input_data, flag_counts, 300.0, 10, 'USA')

    assert table == ['USA', 20, 2, 300.0, 10]



# test geojson writer


# test summary_table_row_generation


# test get_sub_directionaries

