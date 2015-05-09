#!/bin/bash

rm /Users/adrianaciccone/Documents/UChicago/2014-2015/Thesis/thesis/VintResults/*


python write.py 1
pyomo solve pyomoVintageMin.py --json --save-results VintResults/simpleResult.json --summary
python vintagePostProcess.py


#python write.py 100
#pyomo solve pyomoVintageMin.py --json --save-results VintResults/simpleResult.json #--summary
#python vintagePostProcess.py





