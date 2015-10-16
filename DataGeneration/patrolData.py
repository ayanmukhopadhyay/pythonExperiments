__author__ = 'ayanmukhopadhyay'

import ConfigParser
import numpy as np
from os import listdir
import fiona
from math import ceil,floor
from datetime import datetime
from datetime import timedelta

def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def getAVLData():
    avlPath = ConfigSectionMap(Config, "filePaths")["avlpath"]
    dataAVL = []
    listFileNames = listdir(avlPath)
    for counter in range(0,len(listFileNames)):
        #break for two files while debugging to test code
        if codeMode == "debug":
            print len(dataAVL)
            if counter==4:
                break
        if "npy" in str(listFileNames[counter]):
            dataAVLTemp = np.load(avlPath + listFileNames[counter])
            dataAVL.extend(dataAVLTemp)
    dataAVL = np.array(dataAVL)
    dataAVL = dataAVL[np.argsort(dataAVL[:,2])]
    return dataAVL

def getGridForPatrol(x,y):
    for counterRows in range(grids.shape[0]):
        for counterColumns in range(grids.shape[1]):
            if grids[counterRows][counterColumns][0][0]< x < grids[counterRows][counterColumns][1][0]\
                and grids[counterRows][counterColumns][0][1]< y < grids[counterRows][counterColumns][1][1]:
                return counterRows*counterColumns + counterColumns
    return None




def getGrids():
    grids = np.zeros((numGridsX,numGridsY),dtype=object)#so that the default type is not float. we will store lists
    for counterY in range(numGridsY):
        for counterX in range(numGridsX):
            lowerLeftCoords = (xLow+counterX*gridSize,yLow+counterY*gridSize)
            upperRightCoords = (xLow+counterX*gridSize+gridSize,yLow+counterY*gridSize+gridSize)
            grids[counterX,counterY] = [np.array(lowerLeftCoords),np.array(upperRightCoords)]

    # for counterY in range(numGridsY):
    #     for counterX in range(numGridsX):
    #         print grids[counterX,counterY]
    return grids

def getProportionalCounts(uniqueCars):
    '''
    once a car is found in any grid, we evaluate its total count across
    all grids and save it in counts. For every car encountered, we first
    check counts to see if total count exists, if not, we find it and store
    it here
    '''
    #initialize variables
    gridPoliceCount = np.zeros(len(uniqueCars))#stores the final result. weighted sum of police presence
    counts = {}
    counterGrid=0

    for counter in range(len(uniqueCars)):
        dict = uniqueCars[counter]
        for key in dict:
            if key not in counts:
                #fetch by dictionary.get, if key doesnt exist then return 0
                totalCount= sum([dictionary.get(key,0) for dictionary in uniqueCars])
                #test code to verify above result
                # testCount = 0
                # for counterDict in range(len(uniqueCars)):
                #     testCount += uniqueCars[counterDict].get(key,0)
                #     print testCount
                #update in counts
                counts.update({key:totalCount})
            else:
                totalCount = counts[key]
            gridPoliceCount[counter]+=dict[key]/float(totalCount)
    return gridPoliceCount



def getPatrolByTimeStep():
    rows = grids.shape[0]
    columns = grids.shape[1]
    timeSteps = int(ceil((endTime-startTime).total_seconds()/float(3600)))
    #patrolByTimeStep = np.zeros((timeSteps,rows*columns),dtype=object)
    endTimeLast=0
    # for counterTime in range(timeSteps):
    #     startTimeCurr = startTime + timedelta(total_seconds=counterTime*3600)
    #     endTimeCurr = startTimeCurr + timedelta(total_seconds=3600)
    #     for counterRow in range(rows):
    #         for counterColumn in range(columns):
    for counterTime in range(timeSteps):
        if codeMode=="debug":
            print "counterTime = " + str(counterTime)
        uniqueCars = [dict() for i in range(rows*columns)]
        for counterPatrol in range(endTimeLast,len(patrol)):
            #checkTimeStep for current patrol point
            timeStepCurrPatrol = floor((patrol[counterPatrol][2] - startTime).total_seconds()/float(3600))
            #if patrol is not in current time step, break
            if int(timeStepCurrPatrol)>counterTime:
                break
                endTimeLast=counterPatrol
            #check which grid the patrol point lies in
            if codeMode=="debug":
                print "patrol = " + str(counterPatrol)
            gridCurrPatrol = getGridForPatrol(patrol[counterPatrol][0],patrol[counterPatrol][1])
            #get car number
            carNumber = patrol[counterPatrol][3]
            #if car number is there already, increment counter
            if carNumber in uniqueCars[gridCurrPatrol]:
                uniqueCars[gridCurrPatrol][carNumber]+=1
            #else add the car number to the dictionary and initialize counter
            else:
                uniqueCars[gridCurrPatrol].update({carNumber:1})

        currGridPoliceCount = getProportionalCounts(uniqueCars)
        # if counterTime%100==0:
        #     print counterPatrol
        np.save("patrolByTimeStep"+str(counterTime),currGridPoliceCount)
        print counterTime






'''
Code Start
'''
#read config
Config = ConfigParser.ConfigParser()
Config.read("params.conf")

#code mode?
codeMode = ConfigSectionMap(Config,"codeMode")["codemode"]

#get patrol data
patrol = getAVLData()

#get shape file details
shpFilePath = (str(ConfigSectionMap(Config, "filePaths")["shpfile"]))
fshp = fiona.open(shpFilePath)
bounds = fshp.bounds

#get grids
gridSize = float(ConfigSectionMap(Config,"algorithmDetails")["gridsize"]) * 1609.34 #convert to miles
xLow = bounds[0]
xHigh = bounds[2]
yLow = bounds[1]
yHigh = bounds[3]

numGridsX = int(ceil((xHigh - xLow)/float(gridSize)))
numGridsY = int(ceil((yHigh - yLow)/float(gridSize)))

grids = getGrids()

print "A"
#set time start and end variables
startTime = datetime(2009,1,1,0,0)
endTime = datetime(2009,12,31,0,0)

#divide avl data based on time-steps
patrolPerTimeStep = getPatrolByTimeStep()









