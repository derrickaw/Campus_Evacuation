import sys
import simpy
import numpy as np
import math
import queue
from numpy.random import exponential
from numpy import mean
from heapq import heappush, heappop, heapify
from random import randint
import matplotlib.pyplot as plt


# Globals
X_MEAN_PARKING = 5.0
PARKING_CAP = .5
SCALE = 70/500
CAR_SIZE = 15 * SCALE
POLICE = False
# Event parameters
MEAN_TRAVEL_TIME = 5.0 # seconds
MEAN_WAITING_TIME = 2.0 # seconds
globalTimeList = []
currentRoadCapacities = {}
exit_list = [(723,32),(733,270),(760,555)] # Exit locations - 10th,5th,North Ave
exit_count = {(723,32):0, (733,270):0, (760,555):0} # Count cars exiting
paths = {}
capacityTracker = []
parkingLots = {}

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

    #for item in sorted(intersections_graph):
    #    print (item, intersections_graph[item])

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
Method to return a tuple of x,y coordinates, which is the closest distance to one
of the exit points - this is used for the police scenario. This is the next location a car should
move to.
"""
def provideListOfPossibleMovesPolice(fromNode, toNode):
    availableMoves = []
    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    #print("curCAPDSFRMNODE:", curCapDownstreamFromToNode)
    min_distance = float('infinity')
    min_pair = None
    for nextMove in curCapDownstreamFromToNode:
        if nextMove[1] > 0 and nextMove[0] != fromNode:
            if math.hypot(fromNode[0] - nextMove[0][0], fromNode[1] - nextMove[0][1]) < min_distance:
                min_distance = math.hypot(fromNode[0] - nextMove[0][0], fromNode[1] - nextMove[0][1])
                min_pair = [fromNode, nextMove[0]]
                availableMoves.append(nextMove)
    print("AVAIL MOVES:", availableMoves)
    return availableMoves

"""
Method to return a list of tuples of x,y coordinates, which are all the possible locations that a
car can move to. No left turns are allowed.
"""
def provideListOfPossibleMovesNoLeft(fromNode, toNode):
    availableMoves = []

    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    print("curCAPDSFRMNODE:", curCapDownstreamFromToNode)
    for nextMove in curCapDownstreamFromToNode:
        print("FROMNODE:", fromNode)
        print("FROMNODE[0] - x-coor:", fromNode[0])
        print("NEXTMOVE[0] - x-coor:", nextMove[0])
        # end of if statement to ensure no left moves are made
        if nextMove[1] > 0 and nextMove[0] != fromNode and nextMove[0][0] >= fromNode[0]:
            availableMoves.append(nextMove)
    print("AVAIL MOVES:", availableMoves)
    return availableMoves

"""
Method to return a list of tuples of x,y coordinates, which are all the possible locations that a
car can move to.
"""
def provideListOfPossibleMoves(fromNode, toNode):
    availableMoves = []

    curCapDownstreamFromToNode = currentRoadCapacities[toNode]
    for nextMove in curCapDownstreamFromToNode:
        if nextMove[1] > 0 and nextMove[0] != fromNode:
            availableMoves.append(nextMove)

    return availableMoves


def changeAvailableCapacity(fromNode, ToNode, arriving=True):
    global currentRoadCapacities

    #print ("from,to",fromNode,ToNode)
    curCapDownstreamFromNode = currentRoadCapacities[fromNode]
    #print ("begin",curCapDownstreamFromNode)
    for i in range(len(curCapDownstreamFromNode)):
        if curCapDownstreamFromNode[i][0] == ToNode:
            if arriving:
                curCapDownstreamFromNode[i] = (ToNode, curCapDownstreamFromNode[i][1]-1)
            else:
                curCapDownstreamFromNode[i] = (ToNode, curCapDownstreamFromNode[i][1]+1)


    #print ("end",curCapDownstreamFromNode)


# Create the global queue of car tuples
def globalQueue(parkingDicts):
    global globalTimeList

    for key in parkingDicts:
        #print(key, parkingDicts[key][0])
        X_COUNT = int(parkingDicts[key] * PARKING_CAP)
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


now = 0.0 # Current (logical) simulation time

def schedule (car_tuple, event):
    """
    Schedules a new event `e` at time `t`.
    """
    global globalTimeList
    heappush (globalTimeList, (car_tuple, event))

def arrives (car_tuple):
    """
    Processes an arrival event at time `t` for a system in state `s`.
    Schedules a pumping event if the pump is free. Returns the new
    system state.
    """
    changeAvailableCapacity(car_tuple[1], car_tuple[2], True)
    t_done = car_tuple[0] + MEAN_TRAVEL_TIME
    car_tuple = (t_done, car_tuple[1], car_tuple[2], car_tuple[3])
    schedule (car_tuple, togo)

def togo (car_tuple):
    # TODO: no leftward, check capacity (if exceeds cap, then put back into globalqueue - maybe call schedule again?),
    # check if the event methods make sense and the simulate is properly executing, add shortest distance for POPO and
    # get random route scenario working
    global exit_count

    "figure out where to go"
    if car_tuple[2] in exit_list:
        exit_count[car_tuple[2]] += 1
        departs(car_tuple[1],car_tuple[2])
    else:

        if POLICE:
            #shortest distance
            values = currentRoadCapacities[car_tuple[1]]
            mini_distance_list = []
            for value in values:
                mini_distance_list.append(math.hypot(car_tuple[1][0] - value[0], car_tuple[1][1] - value[1]))

            shortest_distance = min(mini_distance_list)
            car_tuple = (car_tuple[0], car_tuple[2], shortest_distance, car_tuple[3])
        else: # random location
            #print("CURRENT RD CAP IN TOGO:" , currentRoadCapacities)
            #print("TOGO CAR TUP[1] - from:", car_tuple[1])
            #values = currentRoadCapacities[car_tuple[2]]
            values = provideListOfPossibleMovesPolice(car_tuple[1], car_tuple[2])

            # Make car wait, if no choices available
            if len(values) == 0:
                t_done = car_tuple[0] + MEAN_WAITING_TIME
                car_tuple = (t_done, car_tuple[1], car_tuple[2], car_tuple[3])
                departs(car_tuple[1],car_tuple[2])
                schedule(car_tuple, arrives)
            # Choices are available, lets move
            else:
                #print (values)
                random_bound = len(values) - 1
                index = randint(0,random_bound)
                #print (index)
                # check for capacity
                #print (car_tuple)
                if car_tuple[1] not in parkingLots:
                    #print ("parkinglot ",parkingLots)
                    #print (car_tuple[1])
                    departs(car_tuple[1], car_tuple[2])
                car_tuple = (car_tuple[0], car_tuple[2], values[index][0], car_tuple[3])
                paths[car_tuple[3]].append(car_tuple[2])
                #print (car_tuple)

                #if car_tuple[1] != car_tuple[3]: #not in parking lot

                schedule(car_tuple, arrives)


def departs (fromNode, toNode):
    """
    Processes a finished-pumping event at time `t` for a system in
    state `s`. Schedules a pumping event if any cars are waiting.
    Returns the new system state.
    """
    #print("FROM AND TO NODES IN DEPARTS:", fromNode, "===>", toNode)
    #global currentRoadCapacities

    changeAvailableCapacity(fromNode, toNode, False)


    #values = currentRoadCapacities[fromNode]
    #print("TST:", fromNode, ":", toNode)
    #print("VALUES IN DEPART:", values)
    # find to node in the list of value and increase its capacity i.e. it has departed
    # for value in values:
    #     if toNode == value[0]:
    #         inc_cap = value[1] + 1
    #         value = (value[0], inc_cap)




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


def simulate (events):

    # print ("\nFuture event list:\n%s" % str (events))
    # print ("\nt=0: %s" % str (s))
    count = 0

    while events:
        (car_tuple,event) = heappop (events)
        event(car_tuple)
        count += 1
        capacityTracker.append(calcAvailableCapSys())
        if count > 100000:
            break
        #print ("t=%d: event '%s' => '%s'" % (t, e.__name__, str (s)))
    print("count",count)
    print ("each exit count", exit_count)

# A check
def calcAvailableCapSys():
    count = 0

    for key in currentRoadCapacities:
        for queue in currentRoadCapacities[key]:
            count += queue[1]

    return count

# More test code: If everything worked, so should this simulation!

def main():
    args = sys.argv
    global parkingLots
    global currentRoadCapacities

    intersections, parkingLots = readFileAndSetUp(args[1])
    currentRoadCapacities = createQueuingCapacityDict(intersections)

    # Temp for only one parking lot
    newParkingLots = {}
    newParkingLots[(50,87)] = parkingLots[(50,87)]
    print (newParkingLots)


    # Test
    # print (intersections)
    #print ("CURENT ROAD CAP:", currentRoadCapacities)
    # print (parkingLots)
    # print (calculateRoadCapacity((0,0), (10,0), 1))

    globalQueue(newParkingLots)
    print (len(globalTimeList))
    #print("GLOBAL QUEUE:", sorted(globalTimeList))
    simulate (globalTimeList)

    # print (len(paths))
    print("originalTracker",capacityTracker[0])
    print("currentTracker",capacityTracker[-1])

    print (len(globalTimeList))
    #print ("current globaltimelist",globalTimeList)
    #print("(523,229)",currentRoadCapacities[(523,229)])
    #print("(562,32)",currentRoadCapacities[(562,32)])

    # print (capacityTracker)
    # Plot road capacities
    plt.plot(capacityTracker)
    plt.show()

    # Plot paths of cars
    # for key in paths:
    #     dataArray = np.array(paths[key])
    #     transposed = dataArray.T
    #     x,y = transposed
        #plt.plot(x,y)

    #plt.gca().invert_yaxis()
    #plt.show()






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
