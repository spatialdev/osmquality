#!/bin/bash

# input: set up a configure on "name of the folders" (multiple directories).
# 1. determine which the k-d tree is used.
# 2. specify a specific folder.
# 3. the program will perform all sub-folders in that folder.

# declare variables
kdTree_chose=$1
FOLDER_PATH=""
LEVEL=""
COUNT_NUM=""
GRID_PERCENT=""
MAX_COUNT=""
arrays=()

# specify variables depending on mode chose
if [[ $kdTree_chose == "tree_v1" ]]; then
    FOLDER_PATH="$PWD/$2"
    LEVEL=$3
    COUNT_NUM=$4
    GRID_PERCENT=$5
elif [[ $kdTree_chose == "cascade-kdtree" ]]; then
    FOLDER_PATH="$PWD/$2"
    LEVEL=$3
    COUNT_NUM=$4
    GRID_PERCENT=$5
    MAX_COUNT=$6
fi

# determine whether or not the folder exists in the working directory
if [ -d "$FOLDER_PATH" ]; then
    # create a directory in order to store all results 
    if [ ! -d "$PWD/result" ]; then
        mkdir result
    fi

    # grab names of all sub-directories
    cd $FOLDER_PATH
    for x in $(ls); do 
        arrays+=(${x})
    done
    
    # go back the parent directory and run the program given all sub-directories
    cd ..
    for i in "${arrays[@]}" ; do
        #echo "$FOLDER_PATH/$i"
        
        if [ ! -d "$PWD/result/$i" ]; then
            mkdir "$PWD/result/$i"
        fi

        if [[ $kdTree_chose == "tree_v1" ]]; then
            python3 geoProcess.py --folderPath "$FOLDER_PATH/$i" \
            | python3 gridGeneration.py --outFolder "$PWD/result/$i" \
                                        --maxDepth $LEVEL \
                                        --countNum $COUNT_NUM \
                                        --gridPercent $GRID_PERCENT
        elif [[ $kdTree_chose == "cascade-kdtree" ]]; then
            python3 geoProcess.py --folderPath "$FOLDER_PATH/$i" \
            | python3 gridGeneration.py --outFolder "$PWD/result/$i" \
                                        --maxDepth $LEVEL \
                                        --countNum $COUNT_NUM \
                                        --gridPercent $GRID_PERCENT \
                                        --maxCount $MAX_COUNT
        fi
    done
else
    echo "The $1 does not exist !!"
fi

