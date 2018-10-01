# MQM

OpenStreetMap (OSM) data quality is always a concern and frequently a barrier for use when compared to propriety data. Inspired by other OSM mapping projects, the Map Quality Measurement initiative intends to visualize map quality with a heat-map approach by summarizing map error indicators within relevant grids. We are not simply indicating areas that are missing map quality, we are providing insight for prioritization by overlapping social-economic metrics (e.g., population density, road density, etc.) to enable people-first decision-making when deciding where to work on improving map quality and function. The Map Quality Measure (MQM) is a heat-map style representation showing the map quality for a given geographic unit. To make MQM informative, the size and value of each unit used to summarize quality is sensitive to local context. Our project is developing an automated process to find the optimal heat-map grid size and update in response to an update trigger on demand.

# Usage
**Package Installation:** <br />
1. numpy
2. matplotlib
3. Python3
4. area (link: https://github.com/scisco/area)

**To run the program successifully, please follow steps:** <br />
1. create an arbitrary directory storing all sub-directories in the working directory, and put all input sub-directories into it. <br />

2. change a permission of the **shell_script.sh** file by using command `chmod +x shell_script.sh`. <br />

3. run the program: <br />
3.1: To use a vanilla k-d tree (only one k-d tree), please run Command 1: <br />
3.2: To use a cascade approach (two k-d trees), please execute Command 2:

```
Command 1:
./shell_script.sh tree_v1 [name of the arbitrary directory] [maximum depth] [count number] [percentage value]

For example:
./shell_script.sh tree_v1 test_data 10 10 0.9
```

```
Command 2:
./shell_script.sh cascade-kdtree [name of the arbitrary directory] [maximum depth] [count number (1st k-d tree) ] [percentage value] [maximum count (2nd k-d tree)]

For example:
./shell_script.sh cascade-kdtree test_data 10 10 0.9 100
```

Note: <br />
Users can adjust all parameters for both commands, and minimum value of the depth number is 1. <br />

**Output Format:** <br />
The output format of this program is also a geojson format that includes coordinates of all grids <br />
and the number of counts.

**Result:** <br />
The program yields two types of results: histograms and geojson files.
