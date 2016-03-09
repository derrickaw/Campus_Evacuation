import sys
import simpy
import numpy
import math
import queue
from numpy.random import exponential
from numpy import mean
from heapq import heappush, heappop, heapify

# Globals
X_MEAN_PARKING = 5.0
PARKING_CAP = .10
SCALE = 70/500
CAR_SIZE = 15 * SCALE

# Event parameters
MEAN_TRAVEL_TIME = 5.0 # minutes
MEAN_WAITING_TIME = 2.0 # minutes


# tasks
# 1. Have dict going from current node
# 2. Have only available spots
# 3. Include parking


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
    currentRoadCapacities = {}

    # Go through each intersection node in the intersection dictionary
    for intersectionNode in intersections:
        currentRoadCapacities[intersectionNode] = []
        # Go through each downstream node and add capacity
        for downstreamNode, numLanes in intersections[intersectionNode]:
            currentRoadCapacities[intersectionNode].append((downstreamNode,
            calculateRoadCapacity(intersectionNode, downstreamNode, numLanes)))

    return currentRoadCapacities





globalTimeList = []
def globalQueue(parkingDicts):

    for key in parkingDicts:
        #print(key, parkingDicts[key][0])
        X_COUNT = parkingDicts[key][0]
        x_values = exponential (X_MEAN_PARKING, X_COUNT)
        #print("X ~ Exp(%g):" % X_MEAN)
        #for (i, x_i) in enumerate (x_values):
            #print ("  X_%d = %g" % (i, x_i))
        listOfTimeStamps = list(x_values)
        for time in listOfTimeStamps:
            carTuple = (time, key, parkingDicts[key][1], key)
            globalTimeList.append(carTuple)

    heapify(globalTimeList)


now = 0.0 # Current (logical) simulation time
state = {'AtParking': 0          # no. cars at pump or waiting
         , 'AtIntersection': 0       # no. cars at store
         , 'IntersectionFree': True   # True <==> pump is available
        }



def schedule (t, e):
    """
    Schedules a new event `e` at time `t`.
    """
    global events
    print ("  ==> '%s' @ t=%g" % (e.__name__, t))
    heappush (events, (t, e))

def arrives (t, s):
    """
    Processes an arrival event at time `t` for a system in state `s`.
    Schedules a pumping event if the pump is free. Returns the new
    system state.
    """
    # @YOUSE
    s['AtPump'] += 1
    if s['PumpFree']:
            s['PumpFree'] = False
            t_done = t + exponential (MEAN_PUMPING_TIME)
            schedule (t_done, finishes)
    return s

def finishes (t, s):
    """
    Processes a finished-pumping event at time `t` for a system in
    state `s`. Schedules a pumping event if any cars are waiting.
    Returns the new system state.
    """
    # @YOUSE
    s['AtPump'] -= 1
    if s['PumpFree'] > 0:
        #schedule
        schedule (t + exponential (MEAN_PUMPING_TIME), finishes)
    else:
        s['PumpFree'] = True
    s['AtStore'] += 1
    schedule (t + exponential (MEAN_PUMPING_TIME), departs)
    return

def departs (t, s):
    """
    Processes a departure from the station event at
    time `t` for a system in state `s`.
    """
    # @YOUSE
    s['AtStore'] -= 1
    return s




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

from copy import deepcopy

def simulate (events, initial_state):
    s = deepcopy (initial_state)

    print ("\nFuture event list:\n%s" % str (events))
    print ("\nt=0: %s" % str (s))

    while events:
        # @YOUSE: Get event and process it
        (t,e) = heappop (events)
        e (t,s)

        print ("t=%d: event '%s' => '%s'" % (t, e.__name__, str (s)))



# More test code: If everything worked, so should this simulation!
# simulate (events, state)

def main():
    args = sys.argv

    intersections, parkingLots = readFileAndSetUp(args[1])
    currentRoadCapacities = createQueuingCapacityDict(intersections)



    # Test
    # print (intersections)
    # print (currentRoadCapacities)
    # print (parkingLots)
    # print (calculateRoadCapacity((0,0), (10,0), 1))

    #print (intersections)
    #print (parkingLots)
    #print (calculateRoadCapacity((0,0), (10,0), 1))
    #globalQueue(parkingLots)
    #print("GLOBAL QUEUE:", sorted(globalTimeList))
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
