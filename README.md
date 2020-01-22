# Map Quality Measurement (MQM)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=spatialdev_osmquality&metric=alert_status)](https://sonarcloud.io/dashboard?id=spatialdev_osmquality)

OpenStreetMap (OSM) data quality is always a concern and frequently a barrier for use when compared to commercial data. Inspired by other OSM mapping projects, the Map Quality Measurement initiative intends to visualize map quality with a heat-map approach by summarizing map error indicators within relevant grids. We are not simply indicating areas that are missing map quality, we are providing insight for prioritization by overlapping social-economic metrics (e.g., population density, road density, etc.) to enable people-first decision-making when deciding where to work on improving map quality and function. The Map Quality Measure (MQM) is a heat-map style representation showing the map quality for a given geographic unit. To make MQM informative, the size and value of each unit used to summarize quality is sensitive to local context. Our project is developing an automated process to find the optimal heat-map grid size and update in response to an update trigger on demand.

# Usage

Eventually, this project will be on PyPI, which will make the following steps only necessary for development.

**Installing dependencies**

The MQM tool is compatiable with python 3.7. The run from source, first install `pipenv`.

With pip
```
pip install pipenv
```
Or homebrew...
```
brew install pipenv
```
Now you can create a virtual environment with python 3.7.
```
pipenv --python 3.7
```
Activate the virtual environment by typing:
```
pipenv shell
```
And finally, install the MQM dependencies
```
pipenv install
```

**Running MQM**
Locate your [Atlas Checks](https://github.com/osmlab/atlas-checks) data to use as the input for MQM, and execute the following command:

```
python3 -m mqm --input [input directory containing atlas check geometries and boundary files] 
--output [output directory to store results] --maxDepth [maximum tree depth (default = 10)]
--countNum [a count number (default = 10)] --gridPercent [a grid percentage (default = 0.9)]
--maxCount [maximum count to the second k-d tree]

For example:
python3 -m mqm --folderPath ~/desktop/program/test_data
```

Note:

1. Users can adjust all parameters, and minimum value of the depth number is 1.<br />
2. When users specify the maximum count to the second k-d tree, the tool performs the second tree automatically. <br />
3. If you add a geojson file name 'boundary.json' to any of the sub-directories of the input folder, the bounding box 
of the first feature in that file will be used as the bounding box of the folders results.

**Output Format:**

The output format of this program is also a geojson format that includes coordinates of all grids <br />
and the number of counts.

**Result:**

The program yields two types of results: histograms and geojson files.

# Testing

#### Running the test suite

MQM uses [tox](https://tox.readthedocs.io/en/latest/) and [pytest](https://docs.pytest.org/en/latest/index.html) to test. 

We also use `pipenv` to manage our developer environment, keeping it consistent across a variety of machines and local
python environments.

Then, initialize a virtual environment for this project:
```
pipenv install --dev
```

After that, start a `pipenv` shell:
```
pipenv shell
```

Now, referencing `python` uses the developer python environment. We can run tests by simply typing:
```
tox
```

To exit out of the virtual environment, type:
```
exit
```

### Troubleshooting

There is a bug with [certain versions of pip and pipenv](https://github.com/pypa/pipenv/issues/2924#issuecomment-427351356p).
If you find yourself running into errors like `TypeError: 'module' object is not callable`, try upgrading pipenv:
```
pip install --upgrade pipenv
```
