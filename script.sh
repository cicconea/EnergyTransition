
#!/bin/bash

rm /Users/adrianaciccone/Documents/UChicago/2014-2015/Thesis/thesis/jsonResults/*

for i in {1..10}
do
	echo "Beginning run # $i"
	python write.py $i 
	pyomo solve pyomoSimpleMin.py --json --save-results jsonResults/simpleResult_$i.json --summary > jsonResults/modelSummary_$i.txt
done

python simplePostProcess.py