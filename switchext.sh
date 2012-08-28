#! /bin/bash

for f in *.*; do
    [[ -f "$f" ]] || continue

    if [ "py" == ${f##*.} ]; then
	echo "changing $f to ${f%.*}.repy" 
	mv $f "${f%.*}.repy"
    elif [ "repy" == ${f##*.} ]; then
	echo "changing $f to ${f%.*}.py" 
	mv $f "${f%.*}.py"
    fi

done