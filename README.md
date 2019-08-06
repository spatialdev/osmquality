# Map Quality Measurement (MQM)

OpenStreetMap (OSM) data quality is always a concern and frequently a barrier for use when compared to commercial data. Inspired by other OSM mapping projects, the Map Quality Measurement initiative intends to visualize map quality with a heat-map approach by summarizing map error indicators within relevant grids. We are not simply indicating areas that are missing map quality, we are providing insight for prioritization by overlapping social-economic metrics (e.g., population density, road density, etc.) to enable people-first decision-making when deciding where to work on improving map quality and function. The Map Quality Measure (MQM) is a heat-map style representation showing the map quality for a given geographic unit. To make MQM informative, the size and value of each unit used to summarize quality is sensitive to local context. Our project is developing an automated process to find the optimal heat-map grid size and update in response to an update trigger on demand.

# Usage

Eventually, this project will be on PyPI, which will make the following steps only necessary for development.

**Installing dependencies**

To run the MQM tool from source, please install Python3 and `pipenv`. Then, run the following command to install all of the dependencies: <br />
```
pipenv install
```
Activate the virtual environment by typing:
```
pipenv shell
```


**To run the program successfully, please follow steps:** <br />
1. create an arbitrary directory storing all sub-directories, and put all input sub-directories into it. <br />

2. run the program through applying <br />

```
python3 -m mqm --folderPath [a absolute folder path] --maxDepth [maximum tree depth (default = 10)]
--countNum [a count number (default = 10)] --gridPercent [a grid percentage (default = 0.9)]
--maxCount [maximum count to the second k-d tree] --boundary [a geojson feature, output bbox will match feature's]

For example:
python3 -m mqm --folderPath ~/desktop/program/test_data
```

Note:

1. Users can adjust all parameters, and minimum value of the depth number is 1.<br />
2. When users specify the maximum count to the second k-d tree, the tool performs the second tree automatically. <br />

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

First, install `pipenv`:
```
pip install pipenv
```

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
