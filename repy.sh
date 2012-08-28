#! /bin/bash

repypath="/home/stredger/seattle/seattle_repy/repy.py"
repypreppath="/home/stredger/seattle/seattle_repy/repypp.py"
restrpath="./restrictions.test"
torun="out.repy"

toprep=${1}


printf "Combining src into ${torun} ..."
if python ${repypreppath} ${toprep} ${torun}; then

    printf " Complete\nRunning repy\n"
    python ${repypath} ${restrpath} ${torun}
    printf "\nRepy exited with status ${?}\n"

else
    printf " Failed\n"
fi


