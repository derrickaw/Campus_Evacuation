import sys
import simpy
import time
import numpy as np
import math
import queue
from numpy.random import exponential
from numpy import mean
from heapq import heappush, heappop, heapify
from random import randint
import matplotlib.pyplot as plt


# GLOBAL
X_MEAN_PARKING = 15
PARKING_CAPACITY = .25 # DEFAULT
SCALE = 70/500
CAR_SIZE_FT = 15 # DEFAULT is 15' long cars
CAR_SIZE = CAR_SIZE_FT * SCALE # in graph units
RUN_METHOD = 1 # DEFAULT is police option
NUM_SIMULATIONS = 1000 # DEFAULT
# Event parameters
#MEAN_TRAVEL_TIME = 5 # seconds
MEAN_WAITING_TIME = 5 # seconds
globalTimeList = []
currentRoadCapacities = {}
exit_list = [(723,32),(733,270),(760,555)] # Exit locations - 10th,5th,North Ave
exit_count = {(723,32):0, (733,270):0, (760,555):0} # Count cars exiting
paths = {}
capacityTracker = []
parkingLots = {}
BEGIN_SIMULATION = 0.0 # Beginnig simulation time
END_SIMULATION   = 0.0 # Ending simulation time
AVERAGE_CAR_SPEED_MPH = 25 # MPH
AVERAGE_CAR_SPEED_FTS = AVERAGE_CAR_SPEED_MPH * 5280 / 3600 # FT PER SEC

"""
Method to read from the world file and create a basic graph dictionary to pull
from for creating intersection and parking lot nodes.  There are no one lane
roads in this model except from exiting a parking lot.
fileName - name of file to read from
Return - return intersection dictionary of nodes and incoming queues to node
with capacities for each queue (number of lanes) and
parking lots dictionary of nodes with capacties of each.
Intersection Format -  (89, 81): [((86, 129),1), ((50, 87),2)]
Parking Lot Format  -  (86, 149): 1200
"""
def readFileAndSetUp(fileName):
    worldFile = open(fileName,'r')
    worldFile.readline() # Throw Away top line

    intersections_graph = {}
    parking_nodes = {}

    for line in worldFile:
        array = line.split(',')
        typeNode = array[0]
        nodeFrom = (int(array[1]),int(array[2]))
        nodeTo = (int(array[3]),int(array[4]))
        capacity = int(array[5])

        # Street Nodes; lets process these
        if typeNode == 'Street':
            # Add queue for NodeTo to NodeFrom
            if nodeFrom not in intersections_graph:
                intersections_graph[nodeFrom] = []
                intersections_graph[nodeFrom].append((nodeTo,capacity))
            else:
                intersections_graph[nodeFrom].append((nodeTo,capacity))
            # Add queue for NodeFrom to NodeTo
            if nodeTo not in intersections_graph:
                intersections_graph[nodeTo] = []
                intersections_graph[nodeTo].append((nodeFrom,capacity))
            else:
                intersections_graph[nodeTo].append((nodeFrom,capacity))


        # Parking Nodes; lets process these; never allowing a queue to enter
        # parking lot; use one as a capacity holder for roads coming from
        # parking lot
        elif typeNode == 'Parking':
            if nodeFrom not in intersections_graph:
                intersections_graph[nodeFrom] = []
                intersections_graph[nodeFrom].append((nodeTo,1))
            # Shouldn't ever happen, since there is only one parking lot per
            # coordinate, but let's check anyways
            else:
                intersections_graph[nodeFrom].append((nodeTo, 1))

            parking_nodes[nodeFrom] = (capacity) #, nodeTo)

    worldFile.close()

    return intersections_graph, parking_nodes

"""
Method to create dictionary of current and maximum capacities for each queuing
road segment upto a particular intersection.  The dictionary can be accessed by
asking from the dictionary what intersection of queues you want.
intersections - dictionary of intersections for the entire map system
Return - return intersection dictionary of upstream nodes with current and max
queue size.
Intersection Format - (348, 30): [((168, 30), 0, 171), ((380, 35), 0, 30)]
"""
def createQueuingCapacityDict(intersections):
    global currentRoadCapacities

    # Go through each intersection node in the intersection dictionary
    for intersectionNode in intersections:
        currentRoadCapacities[intersectionNode] = []
        # Go through each downstream node and add capacity
        for downstreamNode, numLanes in intersections[intersectionNode]:
            currentRoadCapacities[intersectionNode].append((downstreamNode,
            calculateRoadCapacity(intersectionNode, downstreamNode, numLanes)))

    return currentRoadCapacities

"""
Method to return a tuple of x,y coordinates, which is the closest distance to
one of the exit points - this is used for the police scenario. This is the next
location a car should move to.
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - Next location for car to go to [(x,y)]
"""
def provideListOfPossibleMovesPolice(fromNode, toNode):
    availableMoves = []
    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    #print("curCAPDSFRMNODE:", curCapDownstreamFromToNode)
    #print("FROMNODE (CURR):", fromNode)
    #print("TONODE (CURR):", toNode)
    min_distance = float('infinity')
    min_pair = None
    for nextMove in curCapDownstreamFromToNode:
        if nextMove[1] > 0 and nextMove[0] != fromNode:
            for exitPoint in exit_list:
                temp_min_distance = math.hypot(exitPoint[0] - nextMove[0][0], exitPoint[1] - nextMove[0][1])
                if temp_min_distance < min_distance:
                    min_distance = temp_min_distance
                    min_pair = [exitPoint, nextMove]
                    #print("MIN_DISTANCE:", min_distance)
                    #print("MIN DISTANCE PAIR:", min_pair)
    if min_pair != None:
        availableMoves.append(min_pair[1])
    #print("AVAIL MOVES:", availableMoves)
    #print("")
    return availableMoves

"""
Method to return a list of tuples of x,y coordinates, which are all the possible
locations that a car can move to. No westward turns are allowed within a small
factor. This is an addition to the model that we decided to include for FUN!
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - Next locations for car to go to [(x,y),(x,y),(x,y)]
"""
def provideListOfPossibleMovesNoLeft(fromNode, toNode):
    availableMoves = []

    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    #print("curCAPDSFRMNODE:", curCapDownstreamFromToNode)
    #print("FROMNODE (CURR):", fromNode)
    #print("TONODE (CURR):", toNode)
    for nextMove in curCapDownstreamFromToNode:
        #print("TONODE[0] (CURR) - x-coor:", toNode[0] - 10)
        #print("NEXTMOVE", nextMove[0])
        #print("NEXTMOVE[0][0] - x-coor:", nextMove[0][0])
        # end of if statement to ensure no left moves are made
        if nextMove[1] > 0 and nextMove[0][0] >= toNode[0] - 20:
            availableMoves.append(nextMove)
    #print("AVAIL MOVES:", availableMoves)
    #print("")
    return availableMoves

"""
Method to return a list of tuples of x,y coordinates, which are all the possible
locations that a car can move to. This will represent the random - red flashing
light scenario.
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - Next location for car to go to [(x,y),(x,y),(x,y)]
"""
def provideListOfPossibleMovesRedLight(fromNode, toNode):
    availableMoves = []

    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    for nextMove in curCapDownstreamFromToNode:
        if nextMove[1] > 0:
            availableMoves.append(nextMove)

    return availableMoves



"""
Method to change available capacity in the master queue dictionary based on if
car is arriving or departing from a particular segment of road.
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - None
"""
def changeAvailableCapacity(fromNode, ToNode, arriving=True):
    global currentRoadCapacities

    curCapDownstreamFromNode = currentRoadCapacities[fromNode]
    for i in range(len(curCapDownstreamFromNode)):
        if curCapDownstreamFromNode[i][0] == ToNode:
            if arriving:
                curCapDownstreamFromNode[i] = (ToNode, curCapDownstreamFromNode[i][1]-1)
            else:
                curCapDownstreamFromNode[i] = (ToNode, curCapDownstreamFromNode[i][1]+1)



"""
Method to create global event queue with all cars inserted in at an exponential
random time.
parkingDicts - parking lot dictionary containing the location of each parking
lot and the designated capacity of the parking lot
return - None
"""
# Create the global queue of car tuples
def globalQueue(parkingDicts):
    global globalTimeList

    for key in parkingDicts:
        X_COUNT = int(parkingDicts[key] * PARKING_CAPACITY)
        x_values = exponential (X_MEAN_PARKING, X_COUNT)
        #print("X ~ Exp(%g):" % X_MEAN)
        #for (i, x_i) in enumerate (x_values):
            #print ("  X_%d = %g" % (i, x_i))
        listOfTimeStamps = list(x_values)
        count = 0
        for time in listOfTimeStamps:
            carTuple = (time, key, currentRoadCapacities[key][0][0], (key,count)) #timestamp, from, to, parkinglot
            paths[(key,count)] = []
            count += 1
            #print("CURR RD CAP KEY[0]:", currentRoadCapacities[key][0][0])
            globalTimeList.append((carTuple, togo))
    heapify(globalTimeList)


"""
Method to schedule an event onto the global scheduler
car_tuple - (#timestamp, fromNode, toNode, parkinglot((50,87),car #))
event     - what event (arrives, togo, departs)
return    - None
"""
def schedule (car_tuple, event):
    global globalTimeList
    heappush (globalTimeList, (car_tuple, event))

"""
Method to calculate travel time per road segment based on from node to to node
capacity, car size, and average travel speed.
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - travel time
"""
def calcTravelTime(fromNode, toNode):

    calcTime = 0
    listOfPossibleDownstreamNodes = currentRoadCapacities[fromNode]
    currentCapacityToToNode = 0

    for downstreamNode in listOfPossibleDownstreamNodes:
        if downstreamNode[0] == toNode:
            currentCapacityToToNode = downstreamNode[1]
            break
    calcTime = currentCapacityToToNode * CAR_SIZE_FT / AVERAGE_CAR_SPEED_FTS
    #print ("current capacity:",currentCapacityToToNode)
    return calcTime


"""
Method to simulate arrival of car into road segment
car_tuple - (#timestamp, fromNode, toNode, parkinglot((50,87),car #))
return    - None
"""
def arrives (car_tuple):
    changeAvailableCapacity(car_tuple[1], car_tuple[2], True)
    t_done = car_tuple[0] + calcTravelTime(car_tuple[1],car_tuple[2])#MEAN_TRAVEL_TIME
    car_tuple = (t_done, car_tuple[1], car_tuple[2], car_tuple[3])
    schedule (car_tuple, togo)

"""
Method to simulate togo event of car from one road segment to another road
segment
car_tuple - (#timestamp, fromNode, toNode, parkinglot((50,87),car #))
return    - None
"""
def togo (car_tuple):
    global exit_count
    values = []  # list of possible moves

    # If car has reached an exit point, take car out of simulation
    if car_tuple[2] in exit_list:
        exit_count[car_tuple[2]] += 1
        departs(car_tuple[1],car_tuple[2])
    else:
        # Determine how the possible moves should be determined
        if RUN_METHOD == "police":    # Police option
            values = provideListOfPossibleMovesPolice(car_tuple[1], car_tuple[2])
        elif RUN_METHOD == "noWest":  # No west move option
            values = provideListOfPossibleMovesNoLeft(car_tuple[1], car_tuple[2])
        elif RUN_METHOD == "random":  # Totally random option
            values = provideListOfPossibleMovesRedLight(car_tuple[1], car_tuple[2])

        # Make car wait, if no choices available
        if len(values) == 0:
            t_done = car_tuple[0] + MEAN_WAITING_TIME
            car_tuple = (t_done, car_tuple[1], car_tuple[2], car_tuple[3])
            departs(car_tuple[1],car_tuple[2])
            schedule(car_tuple, arrives)
        # Choices are available, lets move
        else:
            random_bound = len(values) - 1
            index = randint(0,random_bound)

            # Check for leaving parking lot; don't increase capacity if so
            if car_tuple[1] not in parkingLots:
                #print ("parkinglot ",parkingLots)
                #print (car_tuple[1])
                departs(car_tuple[1], car_tuple[2])
            car_tuple = (car_tuple[0], car_tuple[2], values[index][0], car_tuple[3])
            paths[car_tuple[3]].append(car_tuple[2])

            schedule(car_tuple, arrives)

"""
Method to simulate depart event from a road segment
fromNode - Where car is coming from
toNode   - Where car is going to; basically symbolizes road segment
return   - None
"""
def departs (fromNode, toNode):
    #print("FROM AND TO NODES IN DEPARTS:", fromNode, "===>", toNode)
    #global currentRoadCapacities

    changeAvailableCapacity(fromNode, toNode, False)


"""
Method to calculate the capacity for a road between two nodes based on two
end points and number of lanes of road between those two nodes.
firstNode  - firstNode to pull from
secondNode - secondNode to pull from
numLanes   - number of lanes between firstNode and secondNode
Return - return capacity of road between the firstNode and secondNode
"""
def calculateRoadCapacity(firstNode, secondNode, numLanes):
    # Use Euclid distance
    distance = ((firstNode[0] - secondNode[0])**2 +
                (firstNode[1] - secondNode[1])**2)**(0.5)
    numCarsCapacity = (distance * numLanes) // CAR_SIZE

    return int(numCarsCapacity)



"""
Method to start simulation.  Simulation will end once all events are done.
A trigger counter is in place in case user wants to run the totally random
simulation which theortically may never end unless the trigger counter is used.
events - global list of events to work through
"""
def simulate (events):
    global END_SIMULATION
    # print ("\nFuture event list:\n%s" % str (events))
    # print ("\nt=0: %s" % str (s))
    count = 0

    while events:
        (car_tuple,event) = heappop (events)
        if len(events) == 0:
            END_SIMULATION = car_tuple[0]
        event(car_tuple)
        count += 1
        capacityTracker.append(calcAvailableCapSys())
        if count > NUM_SIMULATIONS:
            END_SIMULATION = car_tuple[0]
            break
        #print ("t=%d: event '%s' => '%s'" % (t, e.__name__, str (s)))

    print("Simulations:",count-1)
    print("Simulation Time:",END_SIMULATION-BEGIN_SIMULATION)
    print ("Exit car counts:", exit_count)


"""
Method to check current capacity in master queue dictionary; symbolizes current
capacity on all roads.
return - None
"""
def calcAvailableCapSys():
    count = 0

    for key in currentRoadCapacities:
        for queue in currentRoadCapacities[key]:
            count += queue[1]

    return count


def main():
    args = sys.argv
    global parkingLots
    global currentRoadCapacities
    global RUN_METHOD
    global PARKING_CAPACITY
    global NUM_SIMULATIONS
    acceptableFileFormat = ['csv']
    acceptableScenarios  = ['police', 'noWest', 'random']
    acceptableCapacities = [0.005,1.0]
    acceptablePlotting   = ['capacity','path','both']

    if len(args) != 6:
        print ("Incorrect number of arguments - Format-> python evalSim.py "
               "world2.csv [police, noWest, random] [0.01-1.00] [capacity,path,"
               "or both] [# of simulations]")
        exit(0)

    mapFile = args[1]
    RUN_METHOD = args[2] # 1(Police), 2(No West), 3(Random, Redlight)
    PARKING_CAPACITY = float(args[3])
    plottingMethod = args[4]
    NUM_SIMULATIONS = int(args[5])

    # Check acceptable file format
    if mapFile[-3:] not in acceptableFileFormat:
        print("Not acceptable file format...needs to be '.csv'")
        exit(0)
    # Check acceptable scenario option
    if RUN_METHOD not in acceptableScenarios:
        print("Not acceptable run method...needs to be 'police', 'noWest', or "
              "'random'.")
        exit(0)
    # Check acceptable range of parking capacity
    if PARKING_CAPACITY < acceptableCapacities[0] or PARKING_CAPACITY > \
        acceptableCapacities[1]:
        print("Parking capacity has to be between 0.005 and 1.00, inclusive.")
        exit(0)
    # Check acceptable plotting method
    if plottingMethod not in acceptablePlotting:
        print("Not acceptable print method...needs to be 'capacity', 'path', or"
              "'both'")
        exit(0)
    # Check for simulation counts
    if NUM_SIMULATIONS < 1:
        print("Number of simulations has to be greater than 0")
        exit(0)


    # Create intersections and parking lots dictionary
    intersections, parkingLots = readFileAndSetUp(mapFile)
    # Create current road capacities dictionary
    currentRoadCapacities = createQueuingCapacityDict(intersections)

    #print("travelTime:",calcTravelTime((347,114),(348,30)))

    # Temp for testing only one parking lot
    # newParkingLots = {}
    # newParkingLots[(50,87)] = parkingLots[(50,87)]
    # print (newParkingLots)
    # globalQueue(newParkingLots)

    # Create global event queue to run simulation with
    globalQueue(parkingLots)
    #print (len(globalTimeList))
    #print("GLOBAL QUEUE:", sorted(globalTimeList))

    # Run Simulation
    simulate (globalTimeList)


    print("Starting Road Capacity:",capacityTracker[0])
    print("Final Road Capacity at Simulation Stop Time:",capacityTracker[-1])
    print ("Current cars in global event queue",len(globalTimeList))
    print ("AFTER COMPLETION globaltimelist",globalTimeList)
    #print("(539,212)",currentRoadCapacities[(539,212)])
    #print("(562,32)",currentRoadCapacities[(562,32)])

    # For plotting
    if plottingMethod == "capacity" or plottingMethod == "both":
        # Plot road capacities
        plt.plot(capacityTracker)
        plt.xlabel('Number of Simulations')
        plt.ylabel('Remaining Capacity in Road Network')
        plt.suptitle('Random Condition with 100% Capacity in Parking Lots')
        #plt.savefig('Random-100-Capacity')
        plt.show()
    if plottingMethod == "path" or plottingMethod == "both":
        # Plot paths of cars
        for key in paths:
            dataArray = np.array(paths[key])
            transposed = dataArray.T
            x,y = transposed
            plt.plot(x,y)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.suptitle('Path of Cars in Random Condition with 0.5% Capacity '
                     'in One Parking Lot')
        plt.gca().invert_yaxis()
        #plt.savefig('Random-005-Path')
        plt.show()


    #print("EXIT CT", exit_count)
if __name__=='__main__':
	main()






# class ParkingLot(object):
#     def __init__(self, value, percent):
#         self.total = math.ceil(value * percent)
#
#     def cars(self):
#         X_COUNT = self.total
#         x_values = exponential (X_MEAN, X_COUNT)
#         # print ("X ~ Exp(%g):" % X_MEAN)
#         # for (i, x_i) in enumerate (x_values):
#         #     print ("  X_%d = %g" % (i, x_i))
#
#
#
# class Intersection:
#         def __init__(self, key, value, carSize):
#             self.carsPQ = []
#             for x in range (len(value)):
#                 pq = queue.PriorityQueue(maxsize = (math.sqrt((key[0]-value[x][0])**2 + (key[1]-value[x][1])**2) // CAR_SIZE))
#                 self.carsPQ.append(pq)
#
# parkingDict = {}
# intersectionDict = {}
# for key, value in parkingDict:
#     ParkingLot(value, PARKING_CAP)
#
# for key, value in intersectionDict:
#     Intersection(key, value, CAR_SIZE)
